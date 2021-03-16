"""
    The constraint module include functions to impose the momentum sum rules on the PDFs
"""
import logging
import numpy as np

from n3fit.layers import xDivide, MSR_Normalization, xIntegrator
from n3fit.backends import operations as op
from n3fit.backends import MetaModel


log = logging.getLogger(__name__)


def gen_integration_input(nx):
    """
    Generates a np.array (shaped (nx,1)) of nx elements where the
    nx/2 first elements are a logspace between 0 and 0.1
    and the rest a linspace from 0.1 to 0
    """
    lognx = int(nx / 2)
    linnx = int(nx - lognx)
    xgrid_log = np.logspace(-9, -1, lognx + 1)
    xgrid_lin = np.linspace(0.1, 1, linnx)
    xgrid = np.concatenate([xgrid_log[:-1], xgrid_lin]).reshape(nx, 1)

    spacing = [0.0]
    for i in range(1, nx):
        spacing.append(np.abs(xgrid[i - 1] - xgrid[i]))
    spacing.append(0.0)

    weights = []
    for i in range(nx):
        weights.append((spacing[i] + spacing[i + 1]) / 2.0)
    weights_array = np.array(weights).reshape(nx, 1)

    return xgrid, weights_array


def msr_impose(nx=int(2e3), basis_size=8, mode='All', scaler=None):
    """
        This function receives:
        Generates a function that applies a normalization layer to the fit.
            - fit_layer: the 8-basis layer of PDF which we fit
        The normalization is computed from the direct output of the NN (so the 7,8-flavours basis)
            - final_layer: the 14-basis which is fed to the fktable
        and it is applied to the input of the fktable (i.e., to the 14-flavours fk-basis).
        It uses pdf_fit to compute the sum rule and returns a modified version of
        the final_pdf layer with a normalisation by which the sum rule is imposed

        Parameters
        ----------
            nx: int
                number of points for the integration grid, default: 2000
            basis_size: int
                number of flavours output of the NN, default: 8
            mode: str
                what sum rules to compute (MSR, VSR or All), default: All
            scaler: scaler
                Function to apply to the input. If given the input to the model
                will be a (1, None, 2) tensor where dim [:,:,0] is scaled 
    """

    # 1. Generate the fake input which will be used to integrate
    xgrid, weights_array = gen_integration_input(nx)
    # 1b If a scaler is provided, scale the input xgrid
    if scaler:
        xgrid = scaler(xgrid)

    # 2. Prepare the pdf for integration
    #    for that we need to multiply several flavours with 1/x
    division_by_x = xDivide()

    # 3. Now create the integration layer (the layer that will simply integrate, given some weight
    integrator = xIntegrator(weights_array, input_shape=(nx,))

    # 4. Now create the normalization by selecting the right integrations
    normalizer = MSR_Normalization(input_shape=(basis_size,), mode=mode)

    # 5. Make the xgrid array into a backend input layer so it can be given to the normalization
    xgrid_input = op.numpy_to_input(xgrid)

    # Now prepare a function that takes as input the 8-flavours output of the NN
    # and the 14-flavours after the fk rotation and returns a 14-flavours normalized output
    # note + TODO:
    # the idea was that the normalization should always be applied at the fktable 14-flavours
    # and always computed at the output of the NN (in case one would like to compute it differently)
    # don't think it is a good idea anymore and should be changed to act only on the output to the fktable
    # but will be dealt with in the future.
                            # fitlayer        #final_pdf
    def apply_normalization(layer_fitbasis, layer_pdf):
        """
            layer_fitbasis: output of the NN
            layer_pdf: output for the fktable
        """

        def ultimate_pdf(x):
            x_original = op.op_gather_keep_dims(x, -1, axis=-1)
            pdf_integrand = op.op_multiply([division_by_x(x_original), layer_fitbasis(x)])
            normalization = normalizer(integrator(pdf_integrand))
            return layer_pdf(x)*normalization

        return ultimate_pdf

    return apply_normalization, xgrid_input


# #########
# 
# 
#     def pdf_integrand(x):
#         """ If a scaler is given, the division needs to take only the original input """
#         x_original = op.op_gather_keep_dims(x, -1, axis=-1)
#         res = op.op_multiply([division_by_x(x_original), fit_layer(x)])
#         return res
# 
# 
#     # 4. Now create the normalization by selecting the right integrations
#     normalizer = MSR_Normalization(input_shape=(8,), mode=mode)
# 
#     # 5. Make the xgrid numpy array into a backend input layer so it can be given
#     xgrid_input = op.numpy_to_input(xgrid)
#     normalization = normalizer(integrator(pdf_integrand(xgrid_input)))
# 
#     def ultimate_pdf(x):
#         return op.op_multiply_dim([final_pdf_layer(x), normalization])
# 
#     # Save a reference to xgrid in ultimate_pdf, very useful for debugging
#     ultimate_pdf.ref_xgrid = xgrid_input
# 
#     return ultimate_pdf, xgrid_input
