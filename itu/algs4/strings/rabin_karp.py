# Created for BADS 2018
# See README.md for details
# This is python3
import math
import random


# The following part is borrowed from https://langui.sh/2009/03/07/generating-very-large-primes/
# in an effort to implement the missing long_random_prime() function
def _rabin_miller(n):
    s = n - 1
    t = 0
    while s & 1 == 0:
        s = int(s / 2)
        t += 1
    k = 0
    while k < 128:
        a = random.randrange(2, n - 1)
        # a^s is computationally infeasible.  we need a more intelligent approach
        # v = (a**s)%n
        # python's core math module can do modular exponentiation
        v = pow(a, s, n)  # where values are (num,exp,mod)
        if v != 1:
            i = 0
            while v != (n - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = (v ** 2) % n
        k += 2
    return True


def _is_prime(n):
    # lowPrimes is all primes (sans 2, which is covered by the bitwise and operator)
    # under 1000. taking n modulo each lowPrime allows us to remove a huge chunk
    # of composite numbers from our potential pool without resorting to Rabin-Miller
    lowPrimes = [
        3,
        5,
        7,
        11,
        13,
        17,
        19,
        23,
        29,
        31,
        37,
        41,
        43,
        47,
        53,
        59,
        61,
        67,
        71,
        73,
        79,
        83,
        89,
        97,
        101,
        103,
        107,
        109,
        113,
        127,
        131,
        137,
        139,
        149,
        151,
        157,
        163,
        167,
        173,
        179,
        181,
        191,
        193,
        197,
        199,
        211,
        223,
        227,
        229,
        233,
        239,
        241,
        251,
        257,
        263,
        269,
        271,
        277,
        281,
        283,
        293,
        307,
        311,
        313,
        317,
        331,
        337,
        347,
        349,
        353,
        359,
        367,
        373,
        379,
        383,
        389,
        397,
        401,
        409,
        419,
        421,
        431,
        433,
        439,
        443,
        449,
        457,
        461,
        463,
        467,
        479,
        487,
        491,
        499,
        503,
        509,
        521,
        523,
        541,
        547,
        557,
        563,
        569,
        571,
        577,
        587,
        593,
        599,
        601,
        607,
        613,
        617,
        619,
        631,
        641,
        643,
        647,
        653,
        659,
        661,
        673,
        677,
        683,
        691,
        701,
        709,
        719,
        727,
        733,
        739,
        743,
        751,
        757,
        761,
        769,
        773,
        787,
        797,
        809,
        811,
        821,
        823,
        827,
        829,
        839,
        853,
        857,
        859,
        863,
        877,
        881,
        883,
        887,
        907,
        911,
        919,
        929,
        937,
        941,
        947,
        953,
        967,
        971,
        977,
        983,
        991,
        997,
    ]
    if n >= 3:
        if n & 1 != 0:
            for p in lowPrimes:
                if n == p:
                    return True
                if n % p == 0:
                    return False
            return _rabin_miller(n)
    return False


def long_random_prime(k):
    """Generates a random prime.

    :param k: the desired bit length of the prime
    :returns: a random prime of bit length k

    """
    # k is the desired bit length
    r = 100 * (math.log(k, 2) + 1)  # number of attempts max
    r_ = r
    while r > 0:
        # randrange is mersenne twister and is completely deterministic
        # unusable for serious crypto purposes
        n = random.randrange(2 ** (k - 1), 2 ** (k))
        r -= 1
        if _is_prime(n):
            return n
    return "Failure after " + r_ + " tries."


class RabinKarp:
    """The RabinKarp class finds the first occurence of a pattern string in a
    text string.

    This implementation uses the Monte Carlo version of the Rabin-Karp
    algorithm.

    """

    def __init__(self, pat):
        """Preprocesses the pattern string.

        :param pat: the pattern string

        """
        self.M = len(pat)
        self.R = 256
        self.Q = long_random_prime(32)
        self.RM = 1
        for _ in range(1, self.M):
            self.RM = (self.R * self.RM) % self.Q
        self.patHash = self._hash(pat, self.M)  # pattern hash value

    def search(self, txt):
        """Returns the index of the first occurrrence of the pattern string in
        the text string.

        :param txt: the text string
        :return: the index of the first occurrence of the pattern string
        in the text string; N if no such match

        """
        N = len(txt)
        M = self.M
        RM = self.RM
        Q = self.Q
        R = self.R
        patHash = self.patHash
        txtHash = self._hash(txt, M)
        if patHash == txtHash:
            return 0
        for i in range(M, N):
            txtHash = (txtHash + Q - RM * ord(txt[i - M]) % Q) % Q
            txtHash = (txtHash * R + ord(txt[i])) % Q
            if patHash == txtHash:
                if self._check(i - M + 1):
                    return i - M + 1
        return N

    def _check(self, i):
        # Not needed in the Monte Carlo version
        # For Las Vegas, check pat with txt[i:i-M+1]
        return True

    def _hash(self, key, M):
        # Modular hashing using Horner's method
        h = 0
        for j in range(0, M):
            h = (self.R * h + ord(key[j])) % self.Q
        return h


def main():
    """Takes a pattern string and an input string as command-line arguments;
    searches for the pattern string in the text string; and prints the first
    occurrence of the pattern string in the text string.

    Will print the pattern after the end of the string if no match is
    found.

    """
    pat = sys.argv[1]
    txt = sys.argv[2]
    rk = RabinKarp(pat)
    print("text:    {}".format(txt))
    offset = rk.search(txt)
    print("pattern:", end=" ")
    for _ in range(0, offset):
        print("", end=" ")
    print(pat)


if __name__ == "__main__":
    import sys

    main()
