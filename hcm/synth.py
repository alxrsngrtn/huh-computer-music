import numpy as np
from scipy import interpolate


def time(t0, T, sample_rate):
    """Just np.linspace()

    t = [t[0], t[1], t[2], ..., t[n], ..., t[N]].
    t[N] = t0 + N*dt = T
    dt = 1/sample_rate
    """
    t = np.linspace(t0, t0 + T, num=T * sample_rate, dtype=np.float32)
    return t


# OSCILLATORS

def sine_wave(t, f, phi=0, A=1):
    """
    Sine wave: frequency, amplitude, and phase-adjustable oscillator.

    Parameters
    ----------
    t : 1-D array
        Time.
    f : scalar or 1-D array
        Frequency.
    A : scalar or 1-D array
        Amplitude, defaults to 1.
    phi : scalar or 1-D array
        Phase, defaults to 0.

    Returns
    ----------
    out : 1-D array
        Time series array of sine wave.
    """
    x = np.multiply(A, np.sin(np.add(np.multiply(2*np.pi*f, t), phi)))
    return x


def square_wave(t, f, d=.5, phi=0, A=1):
    """
    Square wave: frequency, duty cycle, amplitude, and phase-adjustable oscillator.

    Parameters
    ----------
    t : 1-D array
        Time.
    f : scalar or 1-D array
        Frequency.
    d : scalar or 1-D array
        Duty cycle. Values must fall within [0,1].
        Set d=0.5 for square wave.
    A : scalar or 1-D array
        Amplitude, defaults to 1.
    phi : scalar or 1-D array
        Phase, defaults to 0.

    Returns
    ----------
    out : 1-D array
        Time series array of square or pulse wave.

    """
    x = np.multiply(A, signal.square(np.add(np.multiply(2*np.pi*f, t), phi), d))
    return x


def sawtooth_wave(t, f, d=0, phi=0, A=1):
    """
    Sawtooth wave: frequency, duty cycle, amplitude, and phase-adjustable oscillator.

    Parameters
    ----------
    t : 1-D array
        Time.
    f : scalar or 1-D array
        Frequency.
    d : scalar or 1-D array
        Duty cycle. Values must fall within [0,1].
        Set d=0.5 for triangle wave. d=0 for negative slope sawtooth, d=1 for positive slope sawtooth.
    A : scalar or 1-D array
        Amplitude, defaults to 1.
    phi : scalar or 1-D array
        Phase, defaults to 0.

    Returns
    ----------
    out : 1-D array
        Time series array of triangle or sawtooth wave.

    """
    x = np.multiply(A, signal.sawtooth(np.add(np.multiply(2*np.pi*f, t), phi), d))
    return x


# NOISE
# TODO: derive colors of noise by filtered white noise
# TODO: random walks could go here, or....

def white_noise(t):
    """White noise generated by sampling at random from a uniform distribution.

    """
    N = len(t)
    x = np.random.uniform(-1.0, 1.0, N)
    return x


def brownian_noise(t):
    """Brown noise generated """
    N = len(t)
    dx = np.zeros(N)
    for n in range(0, N):
        dx[n] = np.random.normal(0, scale=np.sqrt(t[n]))
    x = np.zeros(N)
    for n in range(1, len(x)):
        x[n] = x[n - 1] + dx[n]
    return x



# FILTERS: lowpass, highpass, (eventually) bandpass...
# Presently have two different 4th order filters, -24dB/oct
# would be useful to have 1st order as well, -6dB/oct

# what are acceptable values for fc, k?
# need a wrapper to take values in range [0,1]?
def lowpass(x, fc, k, sample_rate=R):
    """
    4th order low pass filter.

    Parameters
    ----------
    x : 1-D array
    fc : scalar or 1-D array
        cutoff frequency of filter
    k : scalar or 1-D array
        scaling factor for product x1*x2
    sample_rate : scalar

    Returns
    ----------
    y4 : 1-D array
    """
    # state variables
    y1 = np.zeros(len(x))
    y2 = np.zeros(len(y1))
    y3 = np.zeros(len(y2))
    y4 = np.zeros(len(y3))
    # define angular frequency
    omega = np.multiply(2*np.pi, fc)
    # initial conditions
    y1[0] = omega[0]/(1+omega[0]) * x[0]
    y2[0] = omega[0]/(1+omega[0]) * y1[0]
    y3[0] = omega[0]/(1+omega[0]) * y2[0]
    y4[0] = omega[0]/(1+omega[0]) * y3[0]
    dt = 1/sample_rate
    for n in range(len(x)-1):
        y1[n+1] = y1[n] + dt * omega[n] * (x[n] - y1[n] - k[n] * y4[n])
        y2[n+1] = y2[n] + dt * omega[n] * (y1[n] - y2[n])
        y3[n+1] = y3[n] + dt * omega[n] * (y2[n] - y3[n])
        y4[n+1] = y4[n] + dt * omega[n] * (y3[n] - y4[n])
    return y4

# what are acceptable values for fc, k?
# need a wrapper to take values in range [0,1]?
def highpass(x, fc, k, sample_rate=R):
    """
    4th order high pass filter.

    Parameters
    ----------
    x : 1-D array
    fc : scalar or 1-D array
        cutoff frequency of filter
    k : scalar or 1-D array
        scaling factor for product x1*x2
    sample_rate : scalar

    Returns
    ----------
    y4 : 1-D array
    """
    # state variables
    y1 = np.zeros(len(x))
    y2 = np.zeros(len(y1))
    y3 = np.zeros(len(y2))
    y4 = np.zeros(len(y3))
    # initial conditions
    y1[0] = x[0]
    y2[0] = y1[0]
    y3[0] = y2[0]
    y4[0] = y3[0]
    dt=1/sample_rate
    alpha = 1/(2*np.pi*dt*fc+1)
    for n in range(len(x)-1):
        y1[n+1] = alpha[n] * (y1[n] + x[n+1] - x[n] - k[n] * y4[n])
        y2[n+1] = alpha[n] * (y2[n] + y1[n+1] - y1[n])
        y3[n+1] = alpha[n] * (y3[n] + y2[n+1] - y2[n])
        y4[n+1] = alpha[n] * (y4[n] + y3[n+1] - y3[n])
    return y4


def amplifier(x1, x2, gain=1, bias=0):
    """
    Mock-voltage controlled amplifier.

    Parameters
    ----------
    x1 : 1-D array
        audio or modulation signal
    x2 : scalar or 1-D array
        audio or modulation signal
    gain : scalar or 1-D array
        scaling factor for product x1*x2
    bias : scalar or 1-D array
        offset

    Returns
    ----------
    y : 1-D array
        Time series array of product of x1 and x2.
        y = (gain * x1 * x2) + bias
    """
    y = np.add(np.multiply(gain, np.multiply(x1, x2)), bias)
    return y


def envelope(gate, A, D, S, R):
    """
    ADSR envelope generator.
    TODO: change envelope parameters continuously!
    """
    # create masks
    attack = np.divide(time(A), A)
    decay = np.subtract(1., np.divide(np.multiply(time(D), S), D))
    release = np.subtract(S, np.divide(np.multiply(time(R), S), R))
    AD = np.concatenate((attack, decay))
    # split up gate signal
    Y = np.array_split(gate, np.where(np.diff(gate)!=0)[0]+1)
    # first chunk special case
    if np.all(Y[0]==1):
        Y[0][0:len(AD)] = AD
        Y[0][len(AD):] = S
    else:
        Y[0] = 0
    # the rest
    for y in Y[1:]:
        if np.all(y==1.):
            y[0:len(AD)] = AD
            y[len(AD)+1:] = S
        else:
            y[0:len(release)] = release
            y[len(release)+1:] = 0
    return np.concatenate(Y)



def normalize(x):
    """
    Linearly scales x to range [-1.0, 1.0].

    Parameters
    ----------
    x : 1-D array

    Returns
    ----------
    y : 1-D array
    """
    y = x/max(x.max(), x.min(), key=abs)
    return y


def gate(x, threshold=.5):
    """
    Takes array x in, sets values below threshold to zero, at or above to 1.

    Parameters
    ----------
    x : 1-D array
    threshold : scalar

    Returns
    ----------
    y : 1-D array
    """
    y = np.piecewise(x, [x<threshold, x>=threshold], [0, 1])
    return y


def sample_and_hold(t, x, hold):
    """
    Sample and hold, for manipulating control signals or bitcrushing audio.
    First performs a zero order interpolation on x, creates a new array with values of x with sample rate 'hold'.
    Then performs another zero order interpolation on that array to fill in the values in between hold intervals.

    Parameters
    ----------
    t : 1-D array
        Time.
    x : 1-D array
        Time series signal.
    hold : scalar
        Sample rate.

    Returns
    ----------
    out : 1-D array
    """
    sh = interpolate.interp1d(t, x, kind='zero', axis=0)
    T = t[-1]
    tsh = time(T, sample_rate=hold)
    xsh = sh(tsh)
    sh = interpolate.interp1d(tsh, xsh, kind='zero', axis=0, fill_value='extrapolate')
    out = sh(t)
    return out

## note, might want uneven spacing of hold intervals (for interesting melodies or whatever)
# crux is in tsh: figure out how to vary spacing of time entries in array
# add optional argument to use this functionality if desired
