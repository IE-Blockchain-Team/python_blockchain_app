class AddressBook:
    def __init__(self):
        self.addrBook = {
        "farm_A": b"-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQChMJf/mB0mUtAIGHJLPeM1ZBk2\nq4vOtjmvlhoA4ZHpm6O9UJags5GELsxHk7my8WDOlb9fpgHM2hue6uY/a6QBuVus\n7ZIqKEm8D/Z9EF6nFxkAgD8tavuRYcDnOEkfRr7Gy7oAdtrbuoIuccu9gRQOpqex\nnYhLPm/d4EvgUEBNYQIDAQAB\n-----END PUBLIC KEY-----",
        "farm_B": b"-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDR7fbY0YixX0IqQHTIFAJOmPa4\n0MmFixcmYXPtA8zhlMbBAnYkIT2V1W6cthRwCcY3MtXJ2fyf5e+wcV8u5tgJ1POa\n0sPUF4ydPbCDh+wXq/5fumqxNH9pNa57b8CtsZMfiV51BbVgmYy1shp2VVoo8m8o\niBiVMq416lrilSBSwwIDAQAB\n-----END PUBLIC KEY-----",
        "delivery_A":b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCx4sgu15iWFv0gMrl19NSJ+Wyg\nNCOag2LjmlFTeYfUAlRenDSJJF7EC+NqmwVgVnKNd23CLQK44/zIQfy0LHp8Lf7o\nY5YdPBlARhGm8o0uRbNWMrrULoVP7dzQ36J5XGRJjVebOVd49crDrTKbGcCLw+5M\nwD8qEuzYsdR4vP6ZUwIDAQAB\n-----END PUBLIC KEY-----',
        "delivery_B": b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCd8sh6m6EihlSthqjOA/PiT5aG\nWj/XrRJXCmjNkQyDcwKSarB994bJmOgHZu6Q35dYYzge88S1cqLdxIbRdSCqlsRH\n+ZvMYbree462Kh85NJftxYi6UWxUek9ST89bpUNMa6Gd1RCc5BuDL8tTySSz2Mm8\nFI6AZpXGznQF86SLkwIDAQAB\n-----END PUBLIC KEY-----',
        "store_A":b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCdZeE+gpg+g2/d3khz/jsB8pRp\nOPyD1UqW4jpY6U/e+Roh+Ppkkd/BwK6WLvBkHGn1G6T7G9AacSSwnRjyJlD04bbb\necobrVlkVeI4OP+5l/q4el9Swz0O8mZ9yrVwuyTKvYvLsArDWxcdiCzgCoDOyFHb\nkUP+D1Vvh0Uz3Ky0BQIDAQAB\n-----END PUBLIC KEY-----',
        "store_B":b'-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDtSsNGEcLF3itjMk43Jvg/x2B\nL4SI7Z6Boyg1scFVT+GnIDyx2UijkTt2ZimKHPe0VLrPO4j8dCrhihW+Zz1qRmZR\nXnzfYb3kdt+BCgXg63t+uWIGfJbTRxss+TnjuyQdbwTrAvgtlqdpWe7e/uqvYl+w\nr59ryw8d9+OJ2FAD+QIDAQAB\n-----END PUBLIC KEY-----',
    }

    def pk_to_name(self, pk):
        """
        Converts public key to name of entity
        """
        for name, value in self.addrBook.items():
            if value == pk:
                return name