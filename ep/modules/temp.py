class Machine:

    def __init__(self, priorities, quantum):
        self.register_x = None
        self.register_y = None
        self.pc = None 
        self.memory = []
        self.scheduler = Machine.Scheduler(priorities, quantum)
        self.quantum = quantum

    def add_proccess(self, proccess):
        address = len(self.memory)
        self.memory.extend(proccess.get_instructions())
        self.scheduler.add_proccess(proccess, address)    

    def execute(self):
        while True:

            if len(self.scheduler.proccess_table.bcps_ready) == 0:
                if len(self.scheduler.proccess_table.bcps_blocked) == 0:
                    break
            
            status = self.scheduler.reset_quantum(self.pc, self.register_x, self.register_y)
            if status == 'exit':
                break
    
            idx = 0
            while(idx < self.quantum and status != 'wait'):

                self.pc = status

                instruction = self.memory[self.pc]
                self.pc += 1
                idx += 1


                if instruction == 'SAIR':
                    self.scheduler.finish_proccess()
                    break
                elif instruction == 'E/S':
                    self.schedueler.block_proccess()
                    break
                elif instruction == 'COM':
                    print('COM')
                elif 'X' in instruction:
                    self.register_x = instruction.split(' ')[1]
                    print(f'X: {self.register_x}')
                elif 'Y' in instruction:
                    self.register_y = instruction.split(' ')[1]
                    print(f'Y: {self.register_y}')


                
            

    class Scheduler:

        def __init__(self, priorities, quantum):
            self.priorities = priorities
            self.quantum = quantum
            self.proccess_table = Machine.Scheduler.Proccess_table()
            self.proccesses_qt = 0
            self.nocredits_qt = 0

        def add_proccess(self, proccess, address):
            priority = self.priorities[proccess.get_pid()]
            bcp = Machine.Scheduler.BCP(proccess, address, priority) 
            self.proccess_table.bcps_ready.append(bcp)
            self.proccesses_qt += 1
            

        def sort_bcps_ready(self):
            self.proccess_table.bcps_ready = sorted(self.proccess_table.bcps_ready, key=lambda bcp: bcp.credits)

        def reset_quantum(self, pc, register_x, register_y):


            if self.proccess_table.bcps_ready[0].credits > 0: 
                self.proccess_table.bcps_ready[0].credits -= 1

            if self.proccess_table.bcps_ready[0].credits == 0:
                self.nocredits_qt += 1
                if self.nocredits_qt == self.proccesses_qt:
                    self.reset_credits()

            for proccess in self.proccess_table.bcps_blocked:
                proccess['timeout'] += 1

                if proccess['timeout'] == 2:
                    proccess['bcp'].set_state('ready')
                    self.proccess_table.bcps_ready.append(proccess['bcp'])
                    self.proccess_table.bcps_blocked.remove(proccess)

            self.proccess_table.bcps_ready[0].pc = pc
            self.proccess_table.bcps_ready[0].register_x = register_x
            self.proccess_table.bcps_ready[0].register_y = register_y

            self.sort_bcps_ready()
            
            if len(self.proccess_table.bcps_ready) == 0:
                if len(self.proccess_table.bcps_blocked) == 0:
                    return 'exit'
                else:
                    return 'wait'
                
            return self.proccess_table.bcps_ready[0].pc
        
        def reset_credits(self):
            for bcp in self.proccess_table.bcps_ready:
                bcp.credits = self.priorities[bcp.pid]
            self.nocredits_qt = 0

        
        def finish_proccess(self):
            self.proccess_table.bcps_ready[0].set_state('finished')
            self.proccess_table.bcps_ready.pop(0)
            self.proccesses_qt -= 1

        def block_proccess(self):
            bcp = self.proccess_table.bcps_ready.pop(0)
            bcp.set_state('blocked')
            self.proccess_table.bcps_blocked.append({'bcp': bcp, 'timeout': 0})



        class Proccess_table:

            def __init__(self):
                self.bcps_ready = []
                self.bcps_blocked = []

        class BCP:

            def __init__(self, proccess, address, priority):
                self.name = proccess.get_name()
                self.pid = proccess.get_pid()
                self.pc = address
                self.register_x = None
                self.register_y = None
                self.credits = priority
                self.state = 'ready'

            def set_state(self, state):
                self.state = state
                return