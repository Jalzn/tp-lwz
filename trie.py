from typing import Union, Tuple

class Node:
    def __init__(self):
        self.children = {}  # Dict[str, Node]
        self.code = None
        self.is_end = False
        
class Trie:
    def __init__(self):
        self.root = Node()
        self.size = 0
    
    def _find_common_prefix(self, s1: str, s2: str) -> int:
        """Retorna o tamanho do prefixo comum entre duas strings"""
        i = 0
        min_len = min(len(s1), len(s2))
        while i < min_len and s1[i] == s2[i]:
            i += 1
        return i
    
    def _split_node(self, node: Node, key: str, split_point: int) -> None:
        """Divide um nó em dois no ponto de divisão especificado"""
        new_node = Node()
        
        # Transfere as informações do nó original para o novo nó
        new_node.children = node.children
        new_node.is_end = node.is_end
        new_node.code = node.code
        
        # Reseta o nó original e adiciona o novo nó como filho
        node.children = {key[split_point:]: new_node}
        node.is_end = False
        node.code = None
        
    def insert(self, string: str, code: int) -> None:
        if not string:
            return
            
        node = self.root
        current_key = string
        
        while current_key:
            # Procura um prefixo correspondente nos filhos do nó atual
            matched_prefix = None
            matched_child = None
            
            for prefix, child in node.children.items():
                common_len = self._find_common_prefix(current_key, prefix)
                if common_len > 0:
                    matched_prefix = prefix
                    matched_child = child
                    break
            
            if matched_prefix:
                common_len = self._find_common_prefix(current_key, matched_prefix)
                
                # Se o prefixo comum é menor que o prefixo existente, precisamos dividir o nó
                if common_len < len(matched_prefix):
                    self._split_node(node, matched_prefix, common_len)
                    new_node = Node()
                    new_node.is_end = True
                    new_node.code = code
                    node.children[matched_prefix[:common_len]].children[current_key[common_len:]] = new_node
                    break
                # Se o prefixo comum é igual ao prefixo existente
                elif common_len == len(matched_prefix):
                    node = matched_child
                    current_key = current_key[common_len:]
                    if not current_key:  # Chegamos ao fim da string
                        node.is_end = True
                        node.code = code
                        break
            else:
                # Nenhum prefixo correspondente encontrado, cria um novo nó
                new_node = Node()
                new_node.is_end = True
                new_node.code = code
                node.children[current_key] = new_node
                break
                
        self.size += 1
    
    def search(self, string: str) -> Union[int, None]:
        if not string:
            return None
            
        node = self.root
        current_key = string
        
        while current_key:
            # Procura um prefixo correspondente
            found = False
            for prefix, child in node.children.items():
                if current_key.startswith(prefix):
                    current_key = current_key[len(prefix):]
                    node = child
                    found = True
                    break
            
            if not found:
                return None
                
            if not current_key and node.is_end:  # Chegamos ao fim da string
                return node.code
                
        return None
    
    def get_size(self) -> int:
        return self.size