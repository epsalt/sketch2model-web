import numpy as np
import scipy as sp
from skimage import color, exposure, measure, morphology, segmentation


class Sketch2Model:
    def __init__(self, im, contrast=0.5, closing=5):
        self.initial_image = np.asarray(im)
        self.process(contrast, closing)

    def process(self, contrast, closing):
        """Sketch2Model uses morphological filtering to label regions in a
        hollow sketch and assign them discrete labels"""

        # Compressor
        im = color.rgb2gray(self.initial_image[0:-1:2, 0:-1:2][:, :, :3])
        flt2 = sp.ndimage.filters.gaussian_filter(im**2, 21)
        self.compressed = im / (np.sqrt(flt2))

        # Contrast streching
        p2, p98 = np.percentile(self.compressed, (2, 98))
        self.contrasted = exposure.rescale_intensity(
            self.compressed, in_range=(p2, p98)
        )

        # Binarization with scalar threshold
        self.contrasted_3d = np.stack((self.contrasted,) * 3, axis=-1)
        self.binary = ~(color.rgb2gray(self.contrasted_3d) > contrast)

        # Use binary closing to connect lines that aren't
        # completely crossing
        self.closed = morphology.binary_closing(self.binary, morphology.disk(closing))

        # Remove small objects (bright and dark spots)
        removed = morphology.remove_small_objects(self.closed)
        self.removed = ~morphology.remove_small_objects(~removed)

        # Skeletonize and dilate to get final boundaries
        edges = morphology.skeletonize(self.removed)
        self.skeletonized = ~morphology.dilation(edges, morphology.disk(1))

        # Label regions
        clean_border = segmentation.clear_border(self.skeletonized)
        self.labeled, self.nregions = measure.label(
            clean_border, background=999999, return_num=True
        )
        self.labeled = self.labeled + 1

        # Change border region labels to zero for random walker
        # segmentation in next step
        np.place(self.labeled, np.logical_not(self.skeletonized), 0)  # updates in place

        # Segmentation of border pixels
        self.final = segmentation.random_walker(
            self.skeletonized, self.labeled, beta=1, mode="cg_mg"
        )
