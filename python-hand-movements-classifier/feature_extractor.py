# codded as pressas por @italogsfernandes 13 de dezembro as 5:53 da manhã
# escutando:
# The Spinners - The Rubberband Man,
# The staple singers - Chica Boom
# None of us are free - Solomon Burke
# Logo depois de uma playlist de Sweatting bullets
# Detailled Description:
#    RMS:
#        sqrt(mean(square(vetor)))
#    ZC:
#             a = [ 1,  2,  1,  1, -3, -4,  7,  8,  9, 10, -2,  1, -3,  5,  6,  7,-10]
#        sign() = [ 1,  1,  1,  1, -1, -1,  1,  1,  1,  1, -1,  1, -1,  1,  1,  1, -1]
#        diff() =     [ 0,  0,  0, -2,  0,  2,  0,  0,  0, -2,  2, -2,  2,  0,  0, -2]
#        where() = (array([ 3,  5,  9, 10, 11, 12, 15]),)
#        where()[0].shape[0] = 7
#    The number of zero crossing should be 7, but because sign()
#    returns 0 if 0 is passed, 1 for positive, and -1 for negative values,
#    diff() will count the transition containing zero twice.
#
#   SSC:
#       It uses diff to derivate the signal and obtain the slope
#       So it verifies how many times the slope has changed from a positive
#       number to a negative one.
#       Try uncommenting the next lines and verify:
#        ttt = np.linspace(0,1,1000)
#        xxx = np.sin(2*np.pi*10*ttt) +  0.8*np.sin(2*np.pi*15*ttt) + 0.2*np.sin(2*np.pi*1*ttt)
#
#        ssc_ = np.diff(np.sign(np.diff(xxx)))
#        ssc_ = np.append(ssc_, [0,0])
#        plt.plot(ttt,xxx)
#        plt.plot(ttt,ssc_)
#        ssc_ = np.where(ssc_)[0].shape[0]

import numpy as np # handling numerical data
import pandas as pd

def get_features(input_array,
        features_list = ['RMS', 'ZC', 'MAV', 'VAR', 'WL', 'SSC'],
        output_obj = {}):
    """Get all the features listed in the features list
    Features list made using as reference:
        Nazmi N, Abdul Rahman MA, Yamamoto S-I, Ahmad SA, Zamzuri H, Mazlan SA.
        A Review of Classification Techniques of EMG Signals during Isotonic and
        Isometric Contractions. Postolache OA, Casson A, Mukhopadhyay S, eds.
        Sensors (Basel, Switzerland). 2016;16(8):1304. doi:10.3390/s16081304.

    Parameters
    ----------
    input_array : type
        Description of parameter `input_array`.
    features_list : list
        Available features:
            * 'RMS' : Root Mean Square
            * 'ZC'  : Zero Crossing
            * 'MAV' : Mean Absolute Value
            * 'VAR' : Variance
            * 'WL'  : Wave Length
            * 'SSC' : Slope Signal Change
        Default value setted to all available features
    output_obj : type of object to be returned
        suggestion -> you can utilze pandas dataFrame
                for improve performance in some cases
    Returns
    -------
    dict
        dict with an key for each feature (in lowercase)
    """

    features_list = [f.lower() for f in features_list]

    if 'rms' in features_list:
        output_obj['rms'] = get_rms(input_array)

    if 'zc' in features_list:
        output_obj['zc'] = get_zc(input_array)

    if 'mav' in features_list:
        output_obj['mav'] = get_mav(input_array)

    if 'var' in features_list:
        output_obj['var'] = get_var(input_array)

    if 'wl' in features_list:
        output_obj['wl'] = get_wl(input_array)

    if 'ssc' in features_list:
        output_obj['ssc'] = get_ssc(input_array)

    return output_obj

def get_features_DataFrame(input_array,
        features_list = ['RMS', 'ZC', 'MAV', 'VAR', 'WL', 'SSC']):
    """Get all the features listed in the features list
    Features list made using as reference:
        Nazmi N, Abdul Rahman MA, Yamamoto S-I, Ahmad SA, Zamzuri H, Mazlan SA.
        A Review of Classification Techniques of EMG Signals during Isotonic and
        Isometric Contractions. Postolache OA, Casson A, Mukhopadhyay S, eds.
        Sensors (Basel, Switzerland). 2016;16(8):1304. doi:10.3390/s16081304.

    Parameters
    ----------
    input_array : type
        Description of parameter `input_array`.
    features_list : list
        Available features:
            * 'RMS' : Root Mean Square
            * 'ZC'  : Zero Crossing
            * 'MAV' : Mean Absolute Value
            * 'VAR' : Variance
            * 'WL'  : Wave Length
            * 'SSC' : Slope Signal Change
        Default value setted to all available features
    output_obj : type of object to be returned
        suggestion -> you can utilze pandas dataFrame
                for improve performance in some cases
    Returns
    -------
    dict
        dict with an key for each feature (in lowercase)
    """

    features_list = [f.lower() for f in features_list]
    output_obj = pd.DataFrame(columns=features_list)

    if 'rms' in features_list:
        output_obj['rms'] = get_rms(input_array)

    if 'zc' in features_list:
        output_obj['zc'] = get_zc(input_array)

    if 'mav' in features_list:
        output_obj['mav'] = get_mav(input_array)

    if 'var' in features_list:
        output_obj['var'] = get_var(input_array)

    if 'wl' in features_list:
        output_obj['wl'] = get_wl(input_array)

    if 'ssc' in features_list:
        output_obj['ssc'] = get_ssc(input_array)

    return output_obj

def get_rms(input_array):
    """Root Mean Square (RMS)

    Parameters
    ----------
    input_array : numpy type array
        One-dimentional numpy array
        May work with multi-dimentional arrays, but this wasn't tested

    Returns
    -------
    numpy float64 number
        The result of this operation in the input array.

    """
    return np.sqrt(np.mean(np.square(
       input_array)))

def get_zc(input_array):
    """Zero Crossing (ZC)

    Parameters
    ----------
    input_array : numpy type array
        One-dimentional numpy array
        May work with multi-dimentional arrays, but this wasn't tested

    Returns
    -------
    numpy float64 number
        The result of this operation in the input array.

    """
    s3= np.sign(
     input_array)
    s3[s3==0] = -1     # replace zeros with -1
    return (np.where(np.diff(s3)))[0].shape[0]

def get_mav(input_array):
    """Mean Absolute Value (MAV)

    Parameters
    ----------
    input_array : numpy type array
        One-dimentional numpy array
        May work with multi-dimentional arrays, but this wasn't tested

    Returns
    -------
    numpy float64 number
        The result of this operation in the input array.

    """
    return np.mean(np.abs(
            input_array))

def get_var(input_array):
    """Variance (VAR)

    Parameters
    ----------
    input_array : numpy type array
        One-dimentional numpy array
        May work with multi-dimentional arrays, but this wasn't tested

    Returns
    -------
    numpy float64 number
        The result of this operation in the input array.

    """
    return np.var(
            input_array)

def get_wl(input_array):
    """Wave Lenght (WL)

    Parameters
    ----------
    input_array : numpy type array
        One-dimentional numpy array
        May work with multi-dimentional arrays, but this wasn't tested

    Returns
    -------
    numpy float64 number
        The result of this operation in the input array.

    """
    return np.sum(np.abs(np.diff(
            input_array)))

def get_ssc(input_array):
    """Signal Slop Changes (SSC)

    Parameters
    ----------
    input_array : numpy type array
        One-dimentional numpy array
        May work with multi-dimentional arrays, but this wasn't tested

    Returns
    -------
    numpy float64 number
        The result of this operation in the input array.

    """
    return np.where(np.diff(np.sign(np.diff(
            input_array))))[0].shape[0]
