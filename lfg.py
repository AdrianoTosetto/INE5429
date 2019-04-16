from random import randint
import time
from decimal import Decimal

'''
    caso seja True, os algoritmos de teste de primalidade usarão o randint do
    Python para gerar as testemunhas
'''

PYTHON_RAND = False

'''
    =======================================================================================================
                            Funcoes para geracao de numros pseudoaleatorios
    =======================================================================================================
'''


'''
    Classe: classe utilizada para gerar numeros randomicos de acordo com
    o algoritmo Lagged Fibonacci Generator
    Metodos:
        next: gera o proximo numero randomico. Tipo de retorno: inteiro
    params:
        seed: semente que será usada para gerar os números randomicos, é uma lista
        j: indice do elemento `anterior` analogo ao (i-2) de Fibonacci
        k: indice do elemento `anterior` analogo ao (i-1) de Fibonacci
        bits: tamanho dos numeros gerados em bits
'''

class LaggedFibonacciGenerator:
    def __init__(self, seed = None, j = 3, k = 7, bits = 32):
        self._seed = [0] * k
        if seed is None:
            upper_bound = 0
            lower_bound = 2**(bits-1)
            for i in range(0, bits):
                upper_bound = upper_bound + pow(2, i)
            for i in range(0, k):
                self._seed[i] = randint(lower_bound, upper_bound)
        else:
            self._seed = seed
        self._m = 2**bits
        self._j = j - 1
        self._k = k - 1
        self._bits = bits
        if (len(self._seed) < k):
            print("error, len _seed shoud be, at least, the value of k")
    def next(self):
        _next = (self._seed[self._j] + self._seed[self._k]) % self._m
        if (_next.bit_length() > self._bits):
            diff_bits = (_next.bit_length() - self._bits)
            _next = _next >> diff_bits
        self._seed = self._seed[1:7] + [_next]
        return _next
'''
    source: https://en.wikipedia.org/wiki/Multiply-with-carry_pseudorandom_number_generator,
            https://projecteuclid.org/download/pdf_1/euclid.aoap/1177005878
    Classe: classe utilizada para gerar numeros randomicos de acordo com
    o algoritmo Multiply With Carry
    Metodos:
        next: gera o proximo numero randomico. Tipo de retorno: inteiro
    params:
        bits: tamanho dos numeros gerados em bits

'''

class MultiplyWithCarry:
    def __init__(self, bits):
        self._r = 0xFFFFFFFE
        self._CMWC_CYCLE = 4096
        self._CMWC_C_MAX = 809430660
        self._i = self._CMWC_CYCLE
        self._Q = [0]*4096
        self._c = randint(2, 809430660)
        self._bits = bits

        for i in range(self._CMWC_CYCLE):
            self._Q[i] = randint(2, int(2**(bits-1)))
    def next(self):
        a = 18782
        self._i = (self._i+1) & 4095
        t = a * (self._Q[self._i]) + self._c
        self._c = t >> 32
        x = t + self._c
        if self._c > x:
            x = x+1
            self._c = self._c+1
        aux = (x - self._r)
        if (aux.bit_length() > self._bits):
            diff_bits = (aux.bit_length() - self._bits)
            aux = aux >> diff_bits
        self._Q[self._i] = aux
        return self._Q[self._i]

'''
    Classe: classe utilizada para gerar numeros randomicos de acordo com
    o algoritmo Linear Congruential Generator
    Metodos:
        next: gera o proximo numero randomico. Tipo de retorno: inteiro
    params:
        bits: tamanho dos numeros gerados em bits
        a: multiplicador da formula. Tipo: inteiro
        c: constante a ser somada no calculo do proximo numero. Tipo: inteiro

        os numeros(os valores default, caso o usuário nao passe nada)
        para a, c foram retirados do livro Numerical Recipes
'''

class LinearCongruentialGenerator:
    def __init__(self, seed=None, bits=40, a=1664525, c=1013904223):
        lower_bound = upper_bound = 0
        for i in range(0, bits):
            upper_bound = upper_bound + pow(2, i)
        if seed is None:
            self._seed = int(time.time())
        self._state = int(time.time()) if seed is None else seed
        self._a = randint(lower_bound, upper_bound)
        self._c = randint(lower_bound, upper_bound)
        self._m = 2**(bits+1)
        self._bits = bits
    def next(self):
        _next = (self._a*self._state + self._c) % self._m
        if (_next.bit_length() > self._bits):
            diff_bits = (_next.bit_length() - self._bits)
            _next = _next >> diff_bits
        self._state = _next
        return self._state
'''
    =======================================================================================================
                            Funcoes para teste de primalidade
    =======================================================================================================
'''

'''
    Funcao: miller_rabbin, retorna um booleano. Testa se um numero p
    é primo ou não. True: p é primo com uma boa chance. False: p é composto

    params:
        p: inteiro a ser testado
        k: numero de `testemunhas` que serao ouvidas
'''
def miller_rabbin(n, k):
    if (n % 2 == 0):
        return False
    t = n - 1
    e = 0
    while(t % 2 == 0):
        e = e + 1
        t = t // 2
    m = (n-1) // (2**e)
    #print("t == " + str(t))
    #print("m == " + str(m))
    #print("e == " + str(e))

    for _ in range(k):
        lgc = LinearCongruentialGenerator(bits=n.bit_length()-1)
        a = 0
        if PYTHON_RAND:
            a = randint(2, n - 1)
        else:
            a = lgc.next()
        if a >= n:
            raise("a nao pode ser igual ou maior que o suposto primo N")
        x = pow(a, m, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(e-1):
            x = pow(x, 2, n)
            if x == 1:
                return False
            if x == n - 1:
                break
        else:
            return False
    return True

'''
    Funcao: fermat_primality_test, retorna um booleano. Testa se um numero p
    é primo ou não. True: p é primo com uma boa chance. False: p é composto

    params:
        p: inteiro a ser testado
        k: numero de `testemunhas` que serao ouvidas
'''
def fermat_primality_test(p, k):
    lgc = LinearCongruentialGenerator(bits=p.bit_length()-1)
    if p == 2:
        return True
    if p % 2 == 0:
        return False
    for _ in range(k):
        a = 0
        if PYTHON_RAND:
            a = randint(2, p - 1)
        else:
            a = lgc.next()
        if a >= p:
            raise("a nao pode ser igual ou maior que o suposto primo P")
        if pow(a, p - 1, p) != 1:
            return False
    return True

#print(fermat_primality_test(153002247429829, 10))

bits = [40, 56, 80, 128, 168, 224, 256, 512, 1024, 2048, 4096]
'''
for bit in bits:
    lcg = LinearCongruentialGenerator(bits = bit)
    lfg = LaggedFibonacciGenerator(bits=bit)
    mwc = MultiplyWithCarry(bits=bit)

    start_n1 = time.time()
    n1 = int(lcg.next())
    end_n1 = time.time()

    start_n2 = time.time()
    n2 = int(lfg.next())
    end_n2 = time.time()

    start_n3 = time.time()
    n3 = int(mwc.next())
    end_n3 = time.time()

    t1 = end_n1 - start_n1
    t2 = end_n2 - start_n2
    t3 = end_n3 - start_n3

    print("LinearCongruentialGenerator | bits " + str(bit))
    print("Random = " + "{:.2E}".format(Decimal(str(n1))) + " tempo para gerar" +str(t1))

    #print("LaggedFibonacciGenerator | bits " + str(bit))
    #print("Random = " + "{:.2E}".format(Decimal(str(n2))) + " tempo para gerar " + str(t2))

    #print("MultiplyWithCarry | bits " + str(bit))
    #print("Random = " + "{:.2E}".format(Decimal(str(n3))) + " tempo parar gerar = " +str(t3))
'''
for bit in bits:

    lfg = LaggedFibonacciGenerator(bits=bit)
    find_time_fermat_start = time.time()
    while True:
        x = lfg.next()
        fermat_test_start = time.time()
        if fermat_primality_test(x, 10):
            find_time_fermat_end = fermat_test_end =  time.time()
            diff1 = find_time_fermat_end - find_time_fermat_start
            diff2 = fermat_test_end - fermat_test_start
            print("Numero primo lfg de " + str(bit) + " encontrado em: " + str(diff1))
            print("fermat_primality_test executou em " + str(diff2) + " nro " + str(x))
            break

    lfg = LaggedFibonacciGenerator(bits=bit)
    find_time_miller_rabin_start = time.time()
    while True:
        x = lfg.next()
        miller_rabin_test_start = time.time()
        if miller_rabbin(x, 10):
            find_time_miller_rabin_end = miller_rabin_test_end =  time.time()

            diff1 = find_time_miller_rabin_end - find_time_miller_rabin_start
            diff2 = miller_rabin_test_end - miller_rabin_test_start
            print("Numero primo de lfg " + str(bit) + " encontrado em: " + str(diff1))
            print("miller_rabbin executou em " + str(diff2) + " nro " + str(x))
            break

    lcg = LinearCongruentialGenerator(bits = bit)
    find_time_fermat_start = time.time()
    while True:
        x = lcg.next()
        fermat_test_start = time.time()
        if fermat_primality_test(x, 10):
            find_time_fermat_end = fermat_test_end =  time.time()
            diff1 = find_time_fermat_end - find_time_fermat_start
            diff2 = fermat_test_end - fermat_test_start
            print("Numero primo lcg de " + str(bit) + " encontrado em: " + str(diff1))
            print("fermat_primality_test executou em " + str(diff2) + " nro " + str(x))
            break
    lcg = LinearCongruentialGenerator(bits = bit)
    find_time_miller_rabin_start = time.time()
    while True:
        x = lcg.next()
        miller_rabin_test_start = time.time()
        if miller_rabbin(x, 10):
            find_time_miller_rabin_end = miller_rabin_test_end =  time.time()

            diff1 = find_time_miller_rabin_end - find_time_miller_rabin_start
            diff2 = miller_rabin_test_end - miller_rabin_test_start
            print("Numero primo de lcg " + str(bit) + " encontrado em: " + str(diff1))
            print("miller_rabbin executou em " + str(diff2) + " nro " + str(x))
            break

    mwc = MultiplyWithCarry(bits=bit)
    find_time_fermat_start = time.time()
    while True:
        x = mwc.next()
        fermat_test_start = time.time()
        if fermat_primality_test(x, 10):
            find_time_fermat_end = fermat_test_end =  time.time()
            diff1 = find_time_fermat_end - find_time_fermat_start
            diff2 = fermat_test_end - fermat_test_start
            print("Numero primo mwc de " + str(bit) + " encontrado em: " + str(diff1))
            print("fermat_primality_test executou em " + str(diff2) + " nro " + str(x))
            break

    mwc = MultiplyWithCarry(bits=bit)
    find_time_miller_rabin_start = time.time()
    while True:
        x = mwc.next()
        miller_rabin_test_start = time.time()
        if miller_rabbin(x, 10):
            find_time_miller_rabin_end = miller_rabin_test_end =  time.time()

            diff1 = find_time_miller_rabin_end - find_time_miller_rabin_start
            diff2 = miller_rabin_test_end - miller_rabin_test_start
            print("Numero primo de mwc " + str(bit) + " encontrado em: " + str(diff1))
            print("miller_rabbin executou em " + str(diff2) + " nro " + str(x))
            break
