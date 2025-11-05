class AnyType(str):
    def __eq__(self, _):
        return True
        
    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")