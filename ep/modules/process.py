class Process:
   
    def __init__(self, id):
        
        data = []

        with open(f'processes/{id}.txt', 'r') as file:
            for line in file:
                data.append(line.strip())
        
        self.name = data[0]
        del data[0]
        self.pid = id
        self.instructions = data
        self.state = 'ready'

        return
    
    def get_name(self):
        return self.name
    
    def get_pid(self):
        return self.pid

    def get_instructions(self):
        return self.instructions

    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state
    

        



        
