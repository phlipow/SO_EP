from time import sleep

class Machine:

    def __init__(self, priorities, quantum):
        self.register_x = None
        self.register_y = None
        self.pc = None 
        self.memory = []
        self.scheduler = Machine.Scheduler(priorities, quantum)
        self.quantum = quantum

    def add_process(self, process):
        address = len(self.memory)
        self.memory.extend(process.get_instructions())
        self.scheduler.add_process(process, address)    

    def execute(self):
        while True:

            if len(self.scheduler.process_table.bcps_ready) == 0:
                if len(self.scheduler.process_table.bcps_blocked) == 0:
                    break
            
            
            status = self.scheduler.reset_quantum(self.pc, self.register_x, self.register_y,)
            if status == 'exit':
                break
            self.pc = status
            idx = 0

            while(idx < self.quantum and status != 'wait'):

                sleep(1)
                
                print(f'PC: {self.pc}')
                instruction = self.memory[self.pc]
                self.pc += 1
                idx += 1


                if instruction == 'SAIR':
                    self.scheduler.finish_process()
                    break
                elif instruction == 'E/S':
                    print('E/S')
                    self.pc = self.scheduler.block_process(self.pc, self.register_x, self.register_y)
                elif instruction == 'COM':
                    print('COM')
                elif 'X' in instruction:
                    self.register_x = instruction.split('=')[1]
                    print(f'X: {self.register_x}')
                elif 'Y' in instruction:
                    self.register_y = instruction.split('=')[1]
                    print(f'Y: {self.register_y}')


                
            

    class Scheduler:

        def __init__(self, priorities, quantum):
            self.priorities = priorities
            self.quantum = quantum
            self.process_table = Machine.Scheduler.Process_table()
            self.processes_qt = 0
            self.nocredits_qt = 0

        def add_process(self, process, address):
            priority = self.priorities[process.get_pid()]
            bcp = Machine.Scheduler.BCP(process, address, priority) 
            self.process_table.bcps_ready.append(bcp)
            self.processes_qt += 1
            
        def sort_bcps_ready(self):
            self.process_table.bcps_ready = sorted(self.process_table.bcps_ready, key=lambda bcp: bcp.credits, reverse=True)

        def reset_quantum(self, pc, register_x, register_y):

            if len(self.process_table.bcps_ready) == 0:
                return 'exit'

            if self.process_table.bcps_ready[0].credits > 0: 
                self.process_table.bcps_ready[0].credits -= 1

            if self.process_table.bcps_ready[0].credits == 0:
                self.nocredits_qt += 1
                if self.nocredits_qt == self.processes_qt:
                    self.reset_credits()

            for process in self.process_table.bcps_blocked:
                process['timeout'] += 1

                if process['timeout'] == 3:
                    process['bcp'].state = 'ready'
                    self.process_table.bcps_ready.append(process['bcp'])
                    self.process_table.bcps_blocked.remove(process)

            self.process_table.bcps_ready[0].pc = pc 
            self.process_table.bcps_ready[0].register_x = register_x
            self.process_table.bcps_ready[0].register_y = register_y

            self.sort_bcps_ready()
            
            if len(self.process_table.bcps_ready) == 0:
                if len(self.process_table.bcps_blocked) == 0:
                    return 'exit'
                else:
                    return 'wait'
                
            print(f'process: {self.process_table.bcps_ready[0].name}')
            return self.process_table.bcps_ready[0].pc
        
        def reset_credits(self):
            for bcp in self.process_table.bcps_ready:
                bcp.credits = self.priorities[bcp.pid]
            self.nocredits_qt = 0
        
        def finish_process(self):
            self.process_table.bcps_ready[0].set_state('finished')
            self.process_table.bcps_ready.pop(0)
            self.processes_qt -= 1

        def block_process(self, pc, register_x, register_y):
            self.process_table.bcps_ready[0].pc = pc 
            self.process_table.bcps_ready[0].register_x = register_x
            self.process_table.bcps_ready[0].register_y = register_y
            bcp = self.process_table.bcps_ready[0]
            del self.process_table.bcps_ready[0]
            self.process_table.bcps_blocked.append({'bcp': bcp, 'timeout': 0})
            return self.process_table.bcps_ready[0].pc



        class Process_table:

            def __init__(self):
                self.bcps_ready = []
                self.bcps_blocked = []



        class BCP:

            def __init__(self, process, address, priority):
                self.name = process.get_name()
                self.pid = process.get_pid()
                self.pc = address
                self.register_x = None
                self.register_y = None
                self.credits = priority
                self.state = 'ready'

    def print_lists(self):
        print('ready:')
        for bcp in self.scheduler.process_table.bcps_ready:
            print(f'{bcp.name} ({bcp.credits}) [{bcp.pc}]', end=' | ')
        print(f'\n blocked:')
        for bcp in self.scheduler.process_table.bcps_blocked:
            print(bcp['bcp'].name, '(' + str(bcp['timeout']) + ')', end=' | ')

        print('')