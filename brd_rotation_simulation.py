# To Do
#      Other class Scenarii: run several AvgSimulation with different configurations (Attributes)
#      Ideally, be able to pass the logic of the decision tree as a parameter to the simulation so that we can test several rotations
#      Also, program to read a gearset from a file, reference the stats on that gear from another and run optimisation on gearsets.
# - 

from random import *
import csv
import pprint
import statistics

WSPotency = {'HS': 150.0, 'SS': 140.0, 'BL': 150.0, 'RpS': 80.0, 'BA': 50.0, 'SB': 20.0, 'ME': 190.0, 'VB': 100.0, 'WB': 60.0, 'FA': 0.0}
DoTPotency = {'VB': 35.0, 'WB': 45.0, 'FA': 35.0}

Status_Duration = {'SS': 20.0, 'IR': 15.0, 'BfB': 20.0, 'HE': 20.0, 'RS': 020.0, 'B': 010.0, 'FA': 30.0, 'WB': 18.0, 'VB': 18.0, 'ME': 00.0, 'BL': 00.0, 'SSS': 08.0, 'BA': 00.0, 'RpS': 00.0, 'SB': 00.0}
Status_Cooldown = {'SS': 02.5, 'IR': 60.0, 'BfB': 80.0, 'HE': 90.0, 'RS': 120.0, 'B': 180.0, 'FA': 60.0, 'WB': 02.5, 'VB': 02.5, 'ME': 12.0, 'BL': 15.0, 'SSS': 00.0, 'BA': 30.0, 'RpS': 30.0, 'SB': 40.0}

class Statistics:
    def __init__(self, time):
        self.s = {'nRuns': 0.0, 'Time': time, 'nActions':0.0, 'nCRT': 0.0, 'TotalDmg': 0.0, 'CritDmg': 0.0, 'DotDmg': 0.0, 'UfDotDmg': 0.0, 'CDDmg': 0.0, 'nHS': 0.0, 'nSS': 0.0, 'nDoTTicks': 0.0, 'nBL': 0.0, 'nRoB': 0.0, 'BLDmg': 0.0, 'HSDmg': 0.0, 'SSDmg': 0.0, 'nSSS': 0.0, 'SSSDmg': 0.0, 'AADmg': 0.0}

    def print_statistics(self):
        print('DPS: {:4,.0f}'.format( self.s['TotalDmg'] / self.s['Time']))
        print('Total Damage: {:6,.0f}'.format( self.s['TotalDmg']))
        print('   HS Damage: {:6,.0f} ({:5.1%})'.format( self.s['HSDmg'], self.s['HSDmg'] / self.s['TotalDmg']))
        print('   SS Damage: {:6,.0f} ({:5.1%}) (SSS Damage: {:5.1%}, SSS Procs: {:5.1%})'.format( self.s['SSDmg'], self.s['SSDmg'] / self.s['TotalDmg'], self.s['SSSDmg'] / self.s['SSDmg'], self.s['nSSS'] / self.s['nHS']))
        print('   BL Damage: {:6,.0f} ({:5.1%}) (RoB Procs: {:5.1%})'.format( self.s['BLDmg'], self.s['BLDmg'] / self.s['TotalDmg'], self.s['nRoB'] / self.s['nDoTTicks']))
        print('   AA Damage: {:6,.0f} ({:5.1%})'.format( self.s['AADmg'], self.s['AADmg'] / self.s['TotalDmg']))
        print('  DoT Damage: {:6,.0f} ({:5.1%}) (UF Damage: {:5.1%})'.format( self.s['DotDmg'], self.s['DotDmg'] / self.s['TotalDmg'], self.s['UfDotDmg'] / self.s['DotDmg']))
        print('   CD Damage: {:6,.0f} ({:5.1%})'.format( self.s['CDDmg'], self.s['CDDmg'] / self.s['TotalDmg']))
        print()
        print(' Crit Damage: {:6,.0f} ({:5.1%}) (Critical Hit Rate: {:5.1%}) (excluding DoT Crits)'.format( self.s['CritDmg'], self.s['CritDmg'] / self.s['TotalDmg'], self.s['nCRT'] / self.s['nActions']))

    def dump_statistics(self):
        n = 1

class Statistics_Collection():
    def __init__(self):
        self.sc = []
        self.s = Statistics(0)

    def add(self, i):
        self.sc.append(i)

    def compute(self):
        self.s.s['nRuns'] = len(self.sc)
        self.s.s['Time'] = self.sc[0].s['Time']
        for n in ['nActions', 'nCRT', 'TotalDmg', 'CritDmg', 'DotDmg', 'UfDotDmg', 'CDDmg', 'nHS', 'nSS', 'nDoTTicks', 'nBL', 'nRoB', 'BLDmg', 'HSDmg', 'SSDmg', 'nSSS', 'SSSDmg', 'AADmg']:
            self.s.s[n] = statistics.mean([d.s[n] for d in self.sc if n in d.s])

    def print_statistics(self):
        self.s.print_statistics()

class Simulation:
    _base_gcd_delay = 2.5
    _base_aa_delay = 3.0
    _base_dot_delay = 3.0
    _log_line_keys = ['Time', 'Event', 'Damage', 'RoB', 'SSS', 'isSS', 'isIR', 'isHE', 'isRS', 'isBfB', 'isB', 'isFA', 'isWB', 'isVB']

    def generateGCD_Ticks(self, n):
        l = [0.0]
        for i in range(1,n):
            l.append(l[i-1] + 2.5)
        return l

    def generateoGCD_Ticks(self, n):
        l = [1.25]
        for i in range(1,n):
            l.append(l[i-1] + 2.5)
        return l

    def generateAA_Ticks(self, loop, delay):
        l = [0.0]
        for i in range(1,int(loop / delay + 1)):
            l.append(l[i-1] + delay)
        return l

    def generateDoT_Ticks(self, n):
        l = [0.0]
        for i in range(1,n):
            l.append(l[i-1] + 3.0)
        return l

    def __init__(self, ref, attributes, time, hp=0):
        self._loop = time
        self._attributes = attributes.copy()
        self._adjusted_gcd_delay = 2.5 - self._attributes['SKS'] / 1000
        self._GCD_Ticks = self.generateGCD_Ticks(int(self._loop / self._adjusted_gcd_delay + 1.0))
        self._oGCD_Ticks = self.generateoGCD_Ticks(int(self._loop / self._adjusted_gcd_delay))
        self._AA_Ticks = self.generateAA_Ticks(self._loop, self._base_aa_delay)
        self._DoT_Ticks = self.generateDoT_Ticks(int(self._loop / self._base_dot_delay + 1))

        self._All_Ticks = self._GCD_Ticks + list(set(self._oGCD_Ticks) - set(self._GCD_Ticks))
        self._All_Ticks = self._All_Ticks + list(set(self._AA_Ticks) - set(self._All_Ticks))
        self._All_Ticks = self._All_Ticks + list(set(self._DoT_Ticks) - set(self._DoT_Ticks))
        self._All_Ticks.sort()

        self._was_crit = False
        self._was_rob = False
        self._was_sss = False
        self._status_state =           {'SS': False, 'IR': False, 'BfB': False, 'HE': False, 'RS': False,  'B': False,  'FA': False, 'WB': False, 'VB': False, 'ME': False, 'BL': True,  'SSS': False, 'BA': True,  'RpS': True,  'SB': True}
        self._status_activation_time = {'SS': -2.5,  'IR': -60.0, 'BfB': -80.0, 'HE': -90.0, 'RS': -120.0, 'B': -180.0, 'FA': -60.0, 'WB': -2.5,  'VB': -2.5,  'ME': -12.0, 'BL': -15.0, 'SSS': 0.0,   'BA': -30.0, 'RpS': -30.0, 'SB': -40.0}
        self._dot_status_state =       {'VB':{'SS': False,   'IR': False,    'BfB': False,   'HE': False,    'RS': False}, 'WB':{'SS': False,   'IR': False,    'BfB': False,   'HE': False,    'RS': False}, 'FA':{'SS': False,   'IR': False,    'BfB': False,   'HE': False,    'RS': False}}
        self._statistics = Statistics(time)          
        self._log = []

        self._statistics.s['nRuns'] = ref

    def time_to_expire(self, status,time):
        return max(self._status_activation_time[status] + Status_Duration[status] - time,0.0)

    def time_to_cooldown(self, status,time):
        return max(self._status_activation_time[status] + Status_Cooldown[status] - time,0.0)

    def print_statistics(self):
        self._statistics.print_statistics()
        
    def log(self, name, dmg, time):
        if self._was_crit and name != 'AA':
            self._statistics.s['CritDmg'] += dmg
        if name in ['DoT', 'VB', 'WB']:
            self._statistics.s['DotDmg'] += dmg
        if name in ['VB', 'WB']:
            self._statistics.s['UfDotDmg'] += dmg
        if name == 'BL':
            self._statistics.s['BLDmg'] += dmg
            self._statistics.s['nBL'] += 1        
        if name == 'HS':
            self._statistics.s['HSDmg'] += dmg
            self._statistics.s['nHS'] += 1        
        if name == 'SS' or name == 'SSS':
            self._statistics.s['SSDmg'] += dmg
            self._statistics.s['nSS'] += 1
        if name == 'SSS':
            self._statistics.s['SSSDmg'] += dmg
            self._statistics.s['nSSS'] += 1
        if name == 'AA':
            self._statistics.s['AADmg'] += dmg
        if name == 'DoT' and self._was_rob:
            self._statistics.s['nRoB'] += 1
        if name in ['BA', 'SB', 'RpS']:
            self._statistics.s['CDDmg'] += dmg

        self._statistics.s['TotalDmg'] += dmg
        self._log.append(dict(zip(self._log_line_keys,[ time, name, dmg, self._was_rob, self._was_sss, [self._status_state[x] for x in ('SS', 'IR', 'HE', 'RS', 'BfB', 'B', 'FA', 'WB', 'VB')]])))

    def print_log(self):
        print('Time,Event,Damage,RoB,SSS,SS,IR,HE,RS,BfB,B,FA,WB,VB')
        for line in self._log:
            print('{Time:7.2f},{Event:3},{Damage:4.0f},{RoB:b},{SSS:b},{isSS:b},{isIR:b},{isHE:b},{isRS:b},{isBfB:b},{isB:b},{isFA:b},{isWB:b},{isVB:b}'.format(**line))

    def dump_log(self):
        with open('simulation' + self._statistics['nRuns'] + '_log.csv', 'w') as f:
            w = csv.DictWriter(f, _log_line_keys,lineterminator = "\n")
            w.writeheader()
            w.writerows(self._log)

    def barddamage(self, WSPotency, AA = False, FC = False):
        self._was_crit = False
        damage = 0.0
        c = 1
        
        CRT = self._attributes['CRT']
        DEX = self._attributes['DEX']
        DTR = self._attributes['DTR']
        WD = self._attributes['WD']
        AAWD = self._attributes['AAWD']

        if self._status_state['SS']:
            CRT *= 1.1
        if self._status_state['IR']:
            CRT *= 1.1
        if self._status_state['HE']:
            DEX *= 1.15
        if self._status_state['RS']:
            DEX *= 1.2

        if AA:
            WSPotency = AAWD / WD * 100.0
        if AA and self._status_state['B']:
            c = 3
            
        for i in range(c):
            self._statistics.s['nActions'] += 1
            if FC or random() <= (0.0693 * CRT - 18.486) / 100:
                crit = 1.5
                if not FC:
                    self._statistics.s['nCRT'] += 1
                    self._was_crit = True
            else:
                crit = 1.0
            
            damage += WSPotency / 100.0 * (((0.0032 * DEX + 0.4162) * WD + (0.1 * DEX - 0.3529) + ((DTR - 202) * 0.035)) * crit)

        if self._status_state['BfB']:
            damage *= 1.1
            
        return damage

    def computedotdamage(self, time):
        self._was_rob = False
        damage = 0.0
        CRT = self._attributes['CRT']
        DEX = self._attributes['DEX']
        DTR = self._attributes['DTR']
        WD = self._attributes['WD']

        for i in ['FA', 'WB', 'VB']:
            if self._status_state[i]:
                if self._dot_status_state[i]['SS']:
                    CRT *= 1.1
                if self._dot_status_state[i]['IR']:
                    CRT *= 1.1
                if self._dot_status_state[i]['HE']:
                    DEX *= 1.15
                if self._dot_status_state[i]['RS']:
                    DEX *= 1.2
                bfb_mod = 1.0
                if self._dot_status_state[i]['BfB']:
                    bfb_mod = 1.1
               
                crit = 1.0
                if random() <= (0.0693 * CRT - 18.486) / 100:
                    crit = 1.5
                    if random() >= 0.5:
                        self._status_state['BL'] = True
                        self._status_activation_time['BL'] = -15.0
                        self._was_rob = True
                        
                damage += bfb_mod * DoTPotency[i] / 100.0 * (((0.0032 * DEX + 0.4162) * WD + (0.1 * DEX - 0.3529) + ((DTR - 202) * 0.035)) * crit)
                self._statistics.s['nDoTTicks'] +=1

        return damage

    def update_dot_status(self, name, time):
        self._status_state[name] = True
        self._status_activation_time[name] = time
        for i in ['SS', 'IR', 'HE', 'RS', 'BfB']:
            self._dot_status_state[name][i] = self._status_state[i]
            if name == 'FA' and i in ['RS']:
                self._dot_status_state[name][i] = False

    def update_SSS(self, time):
        self._swas_sss = False
        if random() >= 0.8:
            self._status_state['SSS'] = True
            self._status_activation_time['SSS'] = time
            self._was_sss = True

    def refresh_status(self, time):
        for i in ['SS', 'IR', 'BfB', 'HE', 'RS', 'B', 'FA', 'WB', 'VB', 'SSS']:
            if self._status_state[i] and self.time_to_expire(i, time) == 0.0:
                self._status_state[i] = False
        if i == 'ME':
            n = 1
            
    def action(self, name,time):
        dmg = 0.0
        f = False
        
        if name == 'HS':
            dmg = self.barddamage(WSPotency['HS'], False, False)
            self.update_SSS(time)
        elif name == 'SS':
            dmg = self.barddamage(WSPotency['SS'], False, False)
            self._status_state['SS'] = True
            self._status_activation_time['SS'] = time
        elif name in ['VB', 'WB']:
            dmg = self.barddamage(WSPotency[name], False, False)
            self.update_dot_status(name,time)
        elif name in ['SSS']:
            dmg = self.barddamage(WSPotency['SS'], False, True)
            self._was_sss = False
            self._status_state[name] = False
            self._status_activation_time[name] = 0
            self._status_state['SS'] = True
            self._status_activation_time['SS'] = time
        elif name in ['ME', 'BL', 'BA', 'SB', 'RpS']:
            dmg = self.barddamage(WSPotency[name], False, False)
            self._status_activation_time[name] = time
            if name == 'BL':
                self._was_rob = False
        elif name in ['IR', 'HE', 'RS', 'B', 'BfB']:
            self._status_state[name] = True
            self._status_activation_time[name] = time
        elif name == 'FA':
            self.update_dot_status('FA',time)
        elif name == 'AA':
            dmg = self.barddamage(0,True,False)
        elif name == 'DoT':
            dmg = self.computedotdamage(time)
        else:
            print("Error: unknown action name encountered in action function")
        self.log(name, dmg, time)

    def run(self):
        for i in self._All_Ticks:
            if i in self._GCD_Ticks:
                if not self._status_state['SS'] or self.time_to_expire('SS',i) <= 2.5:
                    self.action('SS',i)
                elif not self._status_state['WB'] or (self.time_to_expire('IR',i) <= 7.5 and self._status_state['IR'] and self.time_to_expire('WB',i) >= Status_Duration['WB'] - 7.5):
                    self.action('WB',i)
                elif not self._status_state['VB'] or (self.time_to_expire('IR',i) <= 5.0 and self._status_state['IR'] and self.time_to_expire('VB',i) >= Status_Duration['VB'] - 7.5):
                    self.action('VB',i)
                elif self._status_state['SSS'] and self.time_to_expire('SSS',i) <= 2.5:
                    self.action('SSS',i)
                elif self.time_to_expire('WB',i) <= 2.5:
                    self.action('WB',i)
                elif self.time_to_expire('VB',i) <= 2.5:
                    self.action('VB',i)
                elif self._status_state['SSS']:
                    self.action('SSS',i)
                else:
                    self.action('HS',i)
            if i in self._oGCD_Ticks:
                if self._status_state['ME'] and self.time_to_cooldown('ME',i) == 0.0:
                    action('ME',i)
                elif self._status_state['BL'] and self.time_to_cooldown('BL',i) == 0.0:
                    self.action('BL',i)
                elif not self._status_state['IR'] and self.time_to_cooldown('IR',i) == 0.0:
                    self.action('IR',i)
                elif not self._status_state['HE'] and self.time_to_cooldown('HE',i) == 0.0:
                    self.action('HE',i)
                elif not self._status_state['FA'] and self.time_to_cooldown('FA',i) == 0.0:
                    self.action('FA',i)
                elif not self._status_state['B'] and self.time_to_cooldown('B',i) == 0.0:
                    self.action('B',i)
                elif not self._status_state['RS'] and self.time_to_cooldown('RS',i) == 0.0:
                    self.action('RS',i)
                elif not self._status_state['BfB'] and self.time_to_cooldown('BfB',i) == 0.0:
                    self.action('BfB',i)
                elif self._status_state['BA'] and self.time_to_cooldown('BA',i) == 0.0:
                    self.action('BA',i)
                elif self._status_state['SB'] and self.time_to_cooldown('SB',i) == 0.0:
                    self.action('SB',i)
                elif self._status_state['RpS'] and self.time_to_cooldown('RpS',i) == 0.0:
                    self.action('RpS',i)
            if i in self._AA_Ticks:
                self.action('AA',i)
            if i in self._DoT_Ticks:
                self.action('DoT', i)
            self.refresh_status(i)

class avgSimulation:
    def __init__(self, n, attributes, time, hp=0):
        self._number = n
        self._attributes = attributes.copy()
        self._time = time
        self._simulations = []
        self._statistics = Statistics_Collection()

    def run(self):
        for i in range(self._number):
            s = Simulation(i, self._attributes, self._time)
            s.run()
            self._simulations.append(s)
            self._statistics.add(s._statistics)
        self._statistics.compute()

    def print_statistics(self):
        self._statistics.print_statistics()
            
def ComputeWeights(BaseAtt):
    si = avgSimulation(100,BaseAtt,300.0)
    si.run()
    for i in {'DEX', 'CRT', 'DTR', 'SKS', 'WD'}:
        curAtt = BaseAtt.copy()
        curAtt[i] = curAtt[i] * 1.01
        s = avgSimulation(100,curAtt,300.0)
        s.run()
        BaseAtt['w'+i] = s.Statistics['TotalDmg'] / s.Statistics['Time']
    tdeltaDEXDPS = BaseAtt['wDEX'] - si.Statistics['TotalDmg'] / s.Statistics['Time'])
    BaseAtt['wWD'] = (BaseAtt['wWD'] - si.Statistics['TotalDmg'] / s.Statistics['Time']) / tdeltaDEXDPS
    BaseAtt['wCRT'] = (BaseAtt['wCRT'] - si.Statistics['TotalDmg'] / s.Statistics['Time']) / tdeltaDEXDPS
    BaseAtt['wDTR'] = (BaseAtt['wDTR'] - si.Statistics['TotalDmg'] / s.Statistics['Time']) / tdeltaDEXDPS
    BaseAtt['wSKS'] = (BaseAtt['wSKS'] - si.Statistics['TotalDmg'] / s.Statistics['Time']) / tdeltaDEXDPS
    BaseAtt['wDEX'] = 1.0
        


Attributes = [{'Name': 'Current', 'DEX': 506.0, 'CRT': 530.0, 'DTR': 276.0, 'SKS': 388.0, 'WD': 41, 'AAWD': 44.84}, \
              {'Name': 'BiS', 'DEX': 579.0, 'CRT': 511.0, 'DTR': 317.0, 'SKS': 408.0, 'WD': 48, 'AAWD': 53.76}, \
              {'Name': 'Current +10% WD', 'DEX': 506.0, 'CRT': 530.0, 'DTR': 276.0, 'SKS': 388.0, 'WD': 45.1, 'AAWD': 49.324}, \
              {'Name': 'Current +10% DEX', 'DEX': 556.6, 'CRT': 530.0, 'DTR': 276.0, 'SKS': 388.0, 'WD': 41, 'AAWD': 44.84}, \
              {'Name': 'Current +10% CHR', 'DEX': 506.0, 'CRT': 583.0, 'DTR': 276.0, 'SKS': 388.0, 'WD': 41, 'AAWD': 44.84}, \
              {'Name': 'Current +10% DTR', 'DEX': 506.0, 'CRT': 530.0, 'DTR': 303.6, 'SKS': 388.0, 'WD': 41, 'AAWD': 44.84}, \
              {'Name': 'Current +10% SKS', 'DEX': 506.0, 'CRT': 530.0, 'DTR': 276.0, 'SKS': 426.8, 'WD': 41, 'AAWD': 44.84}]

for i in Attributes:
    s = avgSimulation(100,i,300.0)
    s.run()
    print("Run for {} set".format(i['Name']))
    s.print_statistics()
    print()
    
ComputeWeights(Attirbutes[1])
