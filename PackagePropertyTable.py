class PackagePropertyTable: 

    def __init__(self, size):
        self.table = []
        self.keys = []
        for i in range(size):
            self.table.append([])

    def create(self, key, value):
        bucket = hash(key) % len(self.table)
        self.table[bucket].append(value)
        self.keys.append(key)

    def read(self, key):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]
        if len(bucket_list) > 0:
            return bucket_list
        else:
            print("No packages found for address, do nothing.")
            return []

    def delete(self, key):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        if bucket in bucket_list:
            bucket_list.remove(bucket)

# class PackagePropertyTable:
#     def __init__(self):
#         self.table = {}

#     def read(self, key): #TODO: lookup
#         try:
#             return self.table[key]
#         except KeyError:
#             print("No Packages found at address: ", key)

#     def create(self, key, value): #TODO: insert
#         if key not in self.table:
#             self.table[key] = []
#         self.table[key].append(value)

#     def delete(self, key): #TODO: w/e 
#         try:
#             del self.table[key]
#         except KeyError:
#             print("No Packages found at address: ", key)
