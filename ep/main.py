from modules.machine import Machine
from modules.process import Process

PRIORITIES = {
        '01': 1,
        '02': 3,
        '03': 2,
        '04': 10,
        '05': 4,
        '06': 6,
        '07': 12,
        '08': 8,
        '09': 8,
        '10': 4
        }

QUANTUM = 3

machine = Machine(priorities=PRIORITIES, quantum=QUANTUM)

pids = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']

for pid in pids:
    process = Process(pid)
    machine.add_process(process)

machine.execute()
