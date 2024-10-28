import configparser
import hashlib
import random
import logging
import pickle
from constants import CHARSETS_SECTION, MAIN_CONFIG_FILE
from algorithm import Algorithm

class GomuhryTree:
    class Node:
        def __init__(self, leaf=True):
            self.leaf = leaf
            self.keys = []
            self.child = []
            self.values = []  # For storing chain heads

    def __init__(self, t):
        self.root = self.Node()
        self.t = t  # Minimum degree

    def insert(self, hash_key, chain_head):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            temp = self.Node(leaf=False)
            self.root = temp
            temp.child.insert(0, root)
            self._split_child(temp, 0)
            self._insert_non_full(temp, hash_key, chain_head)
        else:
            self._insert_non_full(root, hash_key, chain_head)

    def _split_child(self, x, i):
        t = self.t
        y = x.child[i]
        z = self.Node(leaf=y.leaf)
        
        x.keys.insert(i, y.keys[t-1])
        x.values.insert(i, y.values[t-1])
        
        z.keys = y.keys[t:(2*t-1)]
        z.values = y.values[t:(2*t-1)]
        y.keys = y.keys[0:(t-1)]
        y.values = y.values[0:(t-1)]

        if not y.leaf:
            z.child = y.child[t:2*t]
            y.child = y.child[0:t]

        x.child.insert(i+1, z)

    def _insert_non_full(self, x, k, v):
        i = len(x.keys) - 1
        if x.leaf:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            x.keys.insert(i+1, k)
            x.values.insert(i+1, v)
        else:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.child[i].keys) == (2*self.t) - 1:
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_non_full(x.child[i], k, v)

    def search(self, k):
        return self._search(self.root, k)

    def _search(self, x, k):
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if i < len(x.keys) and k == x.keys[i]:
            return x.values[i]
        elif x.leaf:
            return None
        else:
            return self._search(x.child[i], k)

class RainbowTable:
    def load_config(self):
        """Loads configuration from config.ini."""
        logging.basicConfig(
            filename='log/rainbowTable.log',
            level=logging.DEBUG,
        )
        logging.debug("Loading configuration")
        self.config = configparser.ConfigParser()
        self.config.read(MAIN_CONFIG_FILE)
        logging.debug(self.config)

    def __init__(self, algorithm, charset, min_length, max_length,
                 chain_length, number_of_chains):
        """RainbowTable constructor

        Arguments:
                algorithm {string} -- name of hash algorithm used
                charset {string} -- name of charset
                min_length {int} -- minimum passwords length
                max_length {int} -- maximum password length
                chain_length {int} -- chain length
                number_of_chains {int} -- number of chains

        Raises:
                ValueError -- if algorithm is not 'sha1' or 'md5'
                ValueError -- if charset name is not in config file
        """
        self.load_config()

        # Load algorithm
        if algorithm == "sha1":
            self.algorithm = Algorithm.SHA1
        elif algorithm == "md5":
            self.algorithm = Algorithm.MD5
        else:
            raise ValueError("Algorithm not supported")

        # Load charset
        if self.config is not None and charset not in self.config[CHARSETS_SECTION]:
            raise ValueError(
                "Charset not supported. For custom charset, edit the file config/config.ini"
            )
        self.charset = self.config[CHARSETS_SECTION][charset]

        self.min_length = min_length
        self.max_length = max_length
        self.chain_length = chain_length
        self.number_of_chains = number_of_chains

        self.tree = GomuhryTree(t=5)  # Initialize with minimum degree 5
        self.table = {}  # Keep the original table for backward compatibility

    def hash_function(self, plaintext):
        """Returns a string that contains the computed hash of the 
        given string, using the algorithm chosen

        Arguments:
                plaintext {string} -- plaintext to hash

        Returns:
                string -- the hash computed
        """
        if self.algorithm == Algorithm.SHA1:
            return hashlib.sha1(plaintext.encode('utf-8')).digest()
        elif self.algorithm == Algorithm.MD5:
            return hashlib.md5(plaintext.encode('utf-8')).digest()

    def reduce_function(self, hashstring, index):
        """Returns a string that contains the reduced value of the 
        given hash string

        Arguments:
                plaintext {string} -- hash to reduce
                index {int} -- affects the choice of the function
                    (for different index, different function)

        Returns:
                string -- the hash computed
        """
        reduced_value = ""
        pswLength = hashstring[1] % (
            self.max_length - self.min_length + 1) + self.min_length
        for i in range(pswLength):
            value = hashstring[((index + i) % len(hashstring))]
            reduced_value += self.charset[value % len(self.charset)]
        return reduced_value

    def generate_chain(self, password):
        '''Produces a chain starting from a plaintext
        
        Arguments:
            password {string} -- plaintext to start from
        
        Returns:
            string -- the final hash (chain tail)
        '''
        logging.debug("Starting generating chain...")
        reduced = password
        for i in range(self.chain_length):
            hashed = self.hash_function(reduced)
            logging.debug(reduced + " --> " + hashed.hex())
            reduced = self.reduce_function(hashed, i)
        logging.debug(
            "------------------------------------->" + hashed.hex())
        return hashed

    def generate_table(self):
        '''Generates the full table with GomuhryTree optimization and logs each
        password-hash pair to hash.txt.'''
        collisions = 0
        self.table = {}
        
        # Open the file to log hashed passwords
        with open("hash.txt", "w") as file:
            for _ in range(self.number_of_chains):
                # Generate a random password of allowed length
                randomPassword = ''.join(random.choices(
                    self.charset,
                    k=random.randint(self.min_length, self.max_length))
                )

                # Generate the chain tail hash from the random password
                chainTail = self.generate_chain(randomPassword)
                
                # Check for collisions
                if chainTail in self.table:
                    collisions += 1
                self.table[chainTail] = randomPassword
                self.tree.insert(chainTail, randomPassword)  # Insert into GomuhryTree
                
                # Write the password and its final hash to the file
                file.write(f"{randomPassword} -> {chainTail.hex()}\n")
    
        logging.debug("Collisions detected: " + str(collisions))

    def save_to_file(self, filename):
        '''Writes this object on a file
        
        Arguments:
            filename {string} -- output file path
        
        Returns:
            bool -- true if success
        '''
        if filename is None:
            return False
        with open(filename, "wb") as fd:
            if fd.write(pickle.dumps(self)) > 0:
                return True
        return False

    @staticmethod
    def load_from_file(filename):
        '''Loads a RainbowObject previously generated
        
        Arguments:
            filename {string} -- input file path
        
        Raises:
            ValueError -- if the file does not contain a valid object
        
        Returns:
            RainbowTable -- the loaded object
        '''
        with open(filename, 'rb') as inputFile:
            objectLoaded = pickle.load(inputFile)
        if not isinstance(objectLoaded, RainbowTable):
            raise ValueError("The file " + filename +
                             " does not contain a valid table")
        return objectLoaded

    def lookup(self, hash_to_crack):
        '''Looks for a cracked hash with GomuhryTree optimization'''
        hash_to_crack = bytes.fromhex(hash_to_crack)
        result = self.tree.search(hash_to_crack)
        if result is not None:
            logging.debug("First chain matched: " + result + " --> " + hash_to_crack.hex())
            return self.crack(result, hash_to_crack)

        # Existing lookup logic...
        for i in range(self.chain_length-1, -1, -1):
            hashtemp = hash_to_crack
            for j in range(i, self.chain_length):
                reduced = self.reduce_function(hashtemp, j)
                hashtemp = self.hash_function(reduced)
                if hashtemp in self.table:
                    logging.debug(
                        "Cracked! Found password: " + self.table[hashtemp] + 
                        " | Step: " + str(i)
                    )
                    return self.crack(self.table[hashtemp], hash_to_crack)
        return None

    def crack(self, password, hash_to_crack):
        '''Attempts to crack the hash with a known starting password'''
        logging.debug(f"Attempting to crack {hash_to_crack.hex()} starting with {password}")
        reduced = password
        for i in range(self.chain_length):
            hashed = self.hash_function(reduced)
            if hashed == hash_to_crack:
                return reduced
            reduced = self.reduce_function(hashed, i)
        return None
