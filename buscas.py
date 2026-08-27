from aigyminsper.search.search_algorithms import BuscaLargura
from aigyminsper.search.graph import State
from gerar_mapa import gerar_mapa


class AgentSpecification(State):
    def __init__(self, op, matriz):
        # voce sempre deve usar esta chamada para inicializar a superclasse
        super().__init__(op)
        self.matriz = matriz
    
    def minkowsky(p1, p2):
        
    def successors(self):
        successors = []
        #TODO
        return successors
    
    def is_goal(self):
        pass
    
    def description(self):
        return "Descrição do problema"
    
    def cost(self):
        return 1
    
    def env(self):
        #
        # IMPORTANTE: este método não deve apenas retornar uma descrição do environment, mas 
        # deve também retornar um valor que descreva aquele nodo em específico. Pois 
        # esta representação é utilizada para verificar se um nodo deve ou ser adicionado 
        # na lista de abertos.
        #
        # Exemplos de especificações adequadas: 
        # - para o problema do soma 1 e 2: return str(self.number)+"#"+str(self.cost)
        # - para o problema das cidades: return self.city+"#"+str(self.cost())
        #
        # Exemplos de especificações NÃO adequadas: 
        # - para o problema do soma 1 e 2: return str(self.number)
        # - para o problema das cidades: return self.city
        #
        None

def main():
    print('Busca em largura')
    state = AgentSpecification('')
    algorithm = BuscaLargura()
    result = algorithm.search(state)
    if result != None:
        print('Achou!')
        print(result.show_path())
    else:
        print('Nao achou solucao')

if __name__ == '__main__':
    main()