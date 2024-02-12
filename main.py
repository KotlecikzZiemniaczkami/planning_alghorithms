import pandas as pd
import sys

def avg(data: list):
    mean = 0
    for i in data:
        mean += i
    return mean / len(data)

# sorting
def sort_panda_process(frame: pd.DataFrame):
    work_frame = frame.copy()
    work_frame = work_frame.transpose()
    work_frame.sort_values(by = 'phase_duration', ascending=True, inplace=True)
    return work_frame.transpose()

# class to generate raport files and to write new data to raport
class Process:
    def __init__(self, file_name: str, if_cmd: bool):
        # reading the data and building data frame
        names = ['arrival_time', 'phase_duration', 'priority_value', 'how long waiting']
        data = {}
        with open(file_name, 'r') as file:
            for i in range(len(names)):
                data[names[i]] = file.readline().strip().split()
            time_quantum_prior = file.readline().strip().split()
            time_quantum_RR = file.readline().strip().split()
        pid = []
        waiting = []

        # making PID
        for i in range(len(data['arrival_time'])):
            pid.append(i + 1)
            waiting.append(0)
        data['PID'] = pid
        data['how long waiting'] = waiting
        for i in data.keys():
            print(i, len(data[i]))
        self.__operational = pd.DataFrame(data)
        self.__operational.set_index('PID', inplace=True)
        self.__operational = self.__operational.transpose()
        for i in self.__operational.columns:
            self.__operational[i] = self.__operational[i].astype('int32')

        # data to raport
        self.__waiting_time = []
        self.__average_waiting_time = 0
        self.num_of_processess = 0
        self.__if_cmd = if_cmd


    # is adding new process
    def __add_new_process(self, df: pd.DataFrame, ar_time: int, pid):
        next_arrival_time_local = ar_time
        next_phase_duration = int(input('give phase duration: '))
        next_priority_value = int(input('give priority value: '))
        df[pid] = [next_arrival_time_local, next_phase_duration, next_priority_value]

    # First Come, First Served
    def FCFS(self):
        operational_data = self.__operational.transpose().query('arrival_time == 0').copy()

        next_arrival_time = max(operational_data.transpose().loc['arrival_time'].astype('int32'))
        operational_data = operational_data.transpose()
        round = 0
        s_round = min(operational_data.loc['arrival_time'].astype('int32'))
        start_time = round
        while (len(list(operational_data.columns))) > 0:
            print('\nRound nr.', round)
            print(operational_data)
            round += 1
            next_arrival_time += 1
            operational_data.loc['phase_duration', operational_data.columns.min()] -= 1

            # preparing to not expropriate
            kept_column_id = list(operational_data.columns)[0]
            kept_column = operational_data[kept_column_id]
            del operational_data[list(operational_data.columns)[0]]
            # increasing how long waiting and prioritare
            operational_data = operational_data.transpose()
            operational_data['how long waiting'] += 1
            operational_data = operational_data.transpose()
            operational_data.insert(0, kept_column_id, kept_column)

            # deleting if process is finished
            if operational_data.loc['phase_duration', list(operational_data.columns)[0]] == 0:
                self.__waiting_time.append(operational_data.loc['how long waiting', list(operational_data.columns)[0]])
                self.num_of_processess += 1
                del operational_data[list(operational_data.columns)[0]]
                if len(list(operational_data.columns)) == 0:
                    break


            # adding new processes from file
            add_from_file = self.__operational.transpose().query('arrival_time ==' + str(round))
            if len(add_from_file.values) > 0:
                operational_data = operational_data.transpose()
                operational_data = pd.concat([operational_data, self.__operational.transpose().query('arrival_time ==' + str(round))])
                operational_data = operational_data.transpose()

            if self.__if_cmd:
                answer = input('Do You wanna add new process? y/n: ')
                if 'Y' in answer.upper():
                    pid = max(list(self.__operational.columns) + list(operational_data.columns)) + 1
                    self.__add_new_process(operational_data, next_arrival_time, pid)

    # Shortest Job First non-expropriatory
    def SJFn(self):
        # reading for 0. round
        actual_round = 0
        operational_data = self.__operational.transpose().query('arrival_time == ' + str(actual_round)).copy()
        operational_data = operational_data.transpose()
        operational_data = sort_panda_process(operational_data)
        # actual algorithm
        while (len(list(operational_data.columns))) > 0:
            # printing actual round
            print('\nRound nr.', actual_round)
            print(operational_data)
            actual_round += 1
            # decreasing phase duration of actual algorithm
            operational_data.loc['phase_duration', list(operational_data.columns)[0]] -= 1

            # preparing to not expropriate
            kept_column_id = list(operational_data.columns)[0]
            kept_column = operational_data[kept_column_id]
            del operational_data[list(operational_data.columns)[0]]
            # increasing how long waiting and prioritare
            operational_data = operational_data.transpose()
            operational_data['how long waiting'] += 1
            operational_data['priority_value'] += 1
            operational_data = operational_data.transpose()
            operational_data = sort_panda_process(operational_data)
            operational_data.insert(0, kept_column_id, kept_column)

            # deleting if process is finished
            if operational_data.loc['phase_duration', list(operational_data.columns)[0]] == 0:
                self.__waiting_time.append(operational_data.loc['how long waiting', list(operational_data.columns)[0]])
                self.num_of_processess += 1
                del operational_data[list(operational_data.columns)[0]]
                if len(list(operational_data.columns)) == 0:
                    break

            # adding new processes from file
            add_from_file = self.__operational.transpose().query('arrival_time ==' + str(actual_round))
            if len(add_from_file.values) > 0:
                operational_data = operational_data.transpose()
                operational_data = pd.concat(
                    [operational_data, self.__operational.transpose().query('arrival_time ==' + str(actual_round))])
                operational_data = operational_data.transpose()
            # adding new process from user (only if it is to print in cmd/powershell)
            if self.__if_cmd:
                answer = input('Do You wanna add new process? y/n: ')
                if 'Y' in answer.upper():
                    pid = max(list(self.__operational.columns) + list(operational_data.columns)) + 1
                    self.__add_new_process(operational_data, actual_round, pid)

    # this method prepares data for being presented in report
    def preparation_to_presentation(self):
        self.__average_waiting_time = avg(self.__waiting_time)
        print(self.__waiting_time)
        return self.__average_waiting_time

# help in adding to lists elements of raport
def help(p, t, nop):
    t.append(p.preparation_to_presentation())
    nop.append(p.num_of_processess)

# work of simulation
def work(which, file_name, time, num_of_proc, cmd):
    if which == '1':
        print('*' * 10, "FCFS", '*' * 10)
        process = Process(file_name, cmd)
        process.FCFS()
        help(process, time, num_of_proc)
        '''
    elif which == '2':
        proc = ['SJF']
        print('*' * 10, "SJF", '*' * 10)
        process = Process(file_name, cmd)
        process.SJF()
        help(process, time, num_of_proc)
        '''
    elif which == '2':
        proc = ["SJF non-expropriatory"]
        print('*' * 10, "SJF non-expropriatory", '*' * 10)
        process = Process(file_name, cmd)
        process.SJFn()
        help(process, time, num_of_proc)
    elif which == '3':
        proc = ["FCFS",  "SJF non-expropriatory"]
        print('*' * 10, "FCFS", '*' * 10)
        process = Process(file_name, cmd)
        process.FCFS()
        help(process, time, num_of_proc)
        '''
        print('*' * 10, "SJF", '*' * 10)
        process1 = Process(file_name, cmd)
        process1.SJF()
        help(process1, time, num_of_proc)
        '''
        print('*' * 10, "SJF non-expropriatory", '*' * 10)
        process2 = Process(file_name, cmd)
        process2.SJFn()
        help(process2, time, num_of_proc)

# generating raport
def in_txt():
    raport = pd.DataFrame()
    file_name = input('please, enter the file name:')
    time = []
    num_of_proc = []
    print('*'*10, "MAIN MENU", '*'*10)
    print('1. FCFS\n2. SJF non-expropriatory\n3. Test')
    which = input("Który algorytm wykonać? (1/2/3): ")
    with open('raport.txt', 'w') as file:
        # all what in console goes to the file
        sys.stdout = file
        if which == '1':
            proc = ['FCFS']
            '''
        elif which == '2':
            proc = ['SJF']
            '''
        elif which == '2':
            proc = ['SJF non-expropriatory']
        elif which == '3':
            proc = ['FCFS', 'SJF non-expropriatory']
        else:
            quit(10)
        work(which, file_name, time, num_of_proc, False)
        raport['used'] = proc
        raport['average waiting time'] = time
        raport['number of processess'] = num_of_proc
        raport.set_index('used', inplace=True)
        print(raport)

# doing everything in console
def in_console():
    raport = pd.DataFrame()
    file_name = input('please, enter the file name:')
    time = []
    num_of_proc = []
    print('*' * 10, "MAIN MENU", '*' * 10)
    print('1. FCFS\n2. SJF non-expropriatory\n3. Test')
    which = input("Który algorytm wykonać? (1/2/3): ")
    if which == '1':
        proc = ['FCFS']
        '''
    elif which == '2':
        proc = ['SJF']
        '''
    elif which == '2':
        proc = ['SJF non-expropriatory']
    elif which == '3':
        proc = ['FCFS', 'SJF non-expropriatory']
    else:
        quit(10)
    work(which, file_name, time, num_of_proc, True)
    raport['used'] = proc
    raport['average waiting time'] = time
    raport['number of processess'] = num_of_proc
    raport.set_index('used', inplace=True)
    print(raport)


what_to_do = input('do You want see simulation or generate raport? S/r:')
what_to_do = what_to_do.upper()
if what_to_do == 'R':
    in_txt()
else:
    in_console()