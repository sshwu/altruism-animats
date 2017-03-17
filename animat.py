import numpy
import math
import random
#import copy

class Animat:
    def __init__(self, x, y, gender, alt_prob, generation, gen_pop, tot_alt, pop_dist, punish_gene, tot_pun):
        self.age = 0
        self.fitness = 1000
        self.gender = gender
        self.x = x
        self.y = y
        self.direction = random.randint(0,4)
        self.food = 0
        self.strikes = 0
        self.altruist_prob = alt_prob
        self.orig_prob = alt_prob
        self.numChildren = 0
        self.hungerCount = 0
        #self.reciproc_prob = rec_prob
        self.generation = generation
        if self.generation < 75:
            gen_pop[self.gender][self.generation] += 1
            gen_pop[2][self.generation] += 1
            tot_alt[self.gender][self.generation] += self.altruist_prob
            tot_alt[2][self.generation] += self.altruist_prob
            #tot_rec[self.generation] += self.reciproc_prob
            tot_pun[self.generation] += punish_gene
        if self.generation < 50 and (self.generation == 0 or self.generation % 10 == 9):
            dist_index = int(numpy.floor(self.altruist_prob * 20))
            if dist_index < 0: dist_index = 0
            if self.generation == 0:
                pop_dist[self.gender][0][dist_index] += 1
                pop_dist[2][0][dist_index] += 1
            else:
                pop_dist[self.gender][(self.generation+1)/10][dist_index] += 1
                pop_dist[2][(self.generation+1)/10][dist_index] += 1
        self.child = None
        #self.sick = False
        self.holding_food = False #whether animat is holding food
        self.nearest_mate = None #who nearest potential mate is (also used for food)
        #self.nearest_sick = None #for females to find sick males
        self.nearest_hungry = None
        self.nearest_mate_dist = -1 #distance to nearest potential mate
        #self.nearest_sick_dist = -1 #distance to nearest sick male
        self.nearest_hungry_dist = -1
        self.altruist_mode = 0 #lock in decision to help or not
        #self.random_approach_mode = 0
        self.mate_cooldown = 0 #should not be needed
        self.mate_start = (self.generation) * 5000 + 2000
        self.immunities = 0
        self.punish_gene = punish_gene
        
        #action indicators
        self.dead = False #dead or not
        self.strikes = 0 #number of times cheated
        self.approach_mate = False #move closer to nearest potential mate
        #self.approach_sick = False #move closer to nearest sick male
        self.approach_hungry = False
        self.dig_food = False #dig up food underneath current position
        self.random_move = False #move randomly
        self.mate = False
        self.give_food = False
        self.ask_mate = False
        self.given = None
        self.asked = None
        self.expect_recip = False #set to True after an altruistic action
        self.reciprocate = False
        self.heal = False
        #self.protect = False
        self.punish = False
        self.cheat = False
        self.eat = False
        self.punished = False
        self.numCht = 0
        self.numAlt = 0
        self.protected = False
        self.rejected = False
        #self.total_fitness = 0
        self.expect_mate = False
        self.numAccepted = 0
        self.numRejected = 0
    
    def update(self, asking_grid, giving_grid, healing_grid, protect_grid, food_under, punish_grid, busy_grid, animats, gen_pop, tot_alt, time_step, cheat_grid, learning, reject_grid):
        self.age += 1 #increment the age
        if self.child: #if there is a child, increment child's age
            self.child.age += 1
        is_hungry = self.fitness < 750
        if is_hungry and learning > 0:
            self.hungerCount += 1
            if self.hungerCount == 10:
                self.hungerCount = 0
                self.altruist_prob = (self.altruist_prob * (1-learning)) + (self.altruist_prob * 0.975 * learning)
        else:
            self.hungerCount = 0
        self.holding_food = self.food > 0
        self.dead = self.fitness <= 0 or time_step >= (self.generation + 1) * 5000
        self.given = giving_grid[self.y][self.x] #for initiation
        self.asked = asking_grid[self.y][self.x] #for females to see if they've been asked to mate
        self.healed = healing_grid[self.y][self.x] #for reciprocation
        #self.protected = protect_grid[self.y][self.x]
        self.punished = punish_grid[self.y][self.x]
        self.cheated = cheat_grid[self.y][self.x] #to notify of cheating
        self.rejected = reject_grid[self.y][self.x]
        #avg_alt = float(tot_alt[self.generation]) / gen_pop[self.generation]
        alt_offset = 0#(avg_alt*50) - 25
        if not self.dead:
            #if time_step >= self.generation * 7500: self.total_fitness += self.fitness
            self.mate = False
            self.heal = False
            self.cheat = False
            self.reciprocate = False
            #self.protect = False
            self.give_food = False
            self.ask_mate = False
            self.approach_hungry = False
            #self.approach_sick = False
            self.approach_mate = False
            self.dig_food = False
            self.random_move = False
            self.punish = False
            #if self.sick: self.fitness -= 4
            #if self.numCht > self.numAlt: self.fitness -= (self.numCht - self.numAlt) / 2.0
            self.mate_cooldown -= 1
            if self.punished:
                self.numCht += 1
                #self.fitness -= 25
                #print "punished", self.gender, self.x, self.y
                busy_grid[self.y][self.x] = False
                #if learning != 0:
                    #self.altruist_prob += learning * 0.9
                #    self.altruist_prob = (self.altruist_prob * (1-learning)) + ((self.altruist_prob + ((1-self.altruist_prob)/8)) * learning)
                    #if self.child:
                    #    self.child.altruist_prob = (self.child.altruist_prob * (1-(2*learning))) + ((self.child.altruist_prob * 1.1) * 2 * learning)
            if self.rejected:
                reject_grid[self.y][self.x] = False
                self.numRejected += 1
                self.expect_mate = False
                #print "rejected"
                if learning != 0:
                    self.altruist_prob = (self.altruist_prob * (1-learning)) + ((self.altruist_prob + ((1-self.altruist_prob)/2)) * learning)
            elif self.expect_mate:
                self.numAccepted += 1
                self.numChildren += 1
                self.expect_mate = False
            if self.asked:
                male_numCht = self.asked[1]
                male_numAlt = self.asked[2]
                male_x = self.asked[3]
                male_y = self.asked[4]
                x = male_numAlt - male_numCht
                #y = self.numAlt - self.numCht
                #print self.asked
                mate_prob = (math.erf(float(x-alt_offset) / 20) + 1) / 2
                #mate_prob = (0.0005 * pow(x, 3) + 0.5)
                #mate_prob = 0.5
                #mate_prob -= self.altruist_prob
                #mate_prob += 0.5
                decision = random.random()
                #print "female deciding"
                if decision < mate_prob:
                    #print "accepted", decision, mate_prob
                    self.mate = True
                    self.numChildren += 1
                    #asking_grid[self.y][self.x] = None
                else:
                    #print "rejected", decision, mate_prob
                    self.random_move = True
                    asking_grid[self.y][self.x] = None
                    reject_grid[male_y][male_x] = True
                    #print "rejected"
            elif self.given: #FEMALE SPECIFIC
                self.food += 50
                self.hungerCount = 0
                decision = random.random()
                #self.altruist_prob = (self.altruist_prob * (1-learning)) + ((self.altruist_prob + ((1-self.altruist_prob)/8)) * learning)
                #print "given", self.gender, self.x, self.y, self.given
                if decision < self.altruist_prob:
                    self.heal = True
                    self.reciprocate = True
                    if learning != 0:
                        if self.gender == 0:
                            self.altruist_prob = (self.altruist_prob * (1-learning)) + ((self.altruist_prob + ((1-self.altruist_prob)/4)) * learning)
                        else:
                            self.altruist_prob = (self.altruist_prob * (1-learning)) + ((self.altruist_prob + (3*(1-self.altruist_prob)/8)) * learning)
                    #print "heal(r)", self.gender, self.x, self.y, self.given
                else:
                    self.cheat = True
                    #print "cheat", self.gender, self.x, self.y, self.given
            elif self.healed: #reciprocated
                #self.cheat = False
                #if not self.expect_recip: #if healed, give protection in return or ignore
                #    #self.fitness += 45
                #    if self.sick:
                #        self.sick = False
                #        self.fitness += 45
                #    else: #self.immunities += 1
                #        self.fitness += 60
                #    decision = random.random()
                #    #print "healed", self.gender, self.x, self.y, self.healed
                #    if decision < self.altruist_prob: #reciprocate
                #        self.protect = True
                #        #print "protect", self.gender, self.x, self.y, self.healed
                #    else: #cheat
                #        self.cheat = True
                #        #print "cheat", self.gender, self.x, self.y, self.healed
                #else:
                self.fitness += 50
                self.expect_recip = False
                self.numAlt += 1
                #print "healed(r)", self.gender, self.x, self.y, self.healed
                busy_grid[self.y][self.x] = False
                healing_grid[self.y][self.x] = None
                self.random_move = True
                if learning != 0:
                    #self.altruist_prob += learning * 0.9
                    self.altruist_prob = (self.altruist_prob * (1-learning)) + ((self.altruist_prob + ((1-self.altruist_prob)/2)) * learning)
            #elif self.protected: #FEMALE SPECIFIC
            #    #self.fitness += 35
            #    #self.immunities += 1
            #    if self.immunities == 0:
            #        self.immunities = 1
            #        self.fitness += 35
            #    else:
            #        self.fitness += 55
            #    self.numAlt += 1
            #    self.expect_recip = False
            #    busy_grid[self.y][self.x] = False
            #    protect_grid[self.y][self.x] = False
            #    #print "protected", self.gender, self.x, self.y
            #    self.random_move = True
            #    if learning != 0:
            #        #self.altruist_prob += learning * 0.9
            #        self.altruist_prob = (self.altruist_prob * (1-learning)) + learning
            #        #if self.child:
            #        #    self.child.altruist_prob = (self.child.altruist_prob * (1-(2*learning))) + (2*learning)
            elif self.expect_recip and self.cheated: #if cheated, punish
                self.punish = True
                if learning != 0:
                    #self.altruist_prob -= learning
                    if self.gender == 0:
                        self.altruist_prob = (self.altruist_prob * (1-learning)) + (self.altruist_prob / 2 * learning)
                    else:
                        self.altruist_prob = (self.altruist_prob * (1-learning)) + (self.altruist_prob * (3.0 / 8.0) * learning)
                    #if self.child:
                    #    self.child.altruist_prob = (self.child.altruist_prob * (1-(2*learning)))
            elif is_hungry: #if hungry, find food
                if not self.holding_food:
                    if food_under > 0: #dig up
                        self.dig_food = True
                    else: #random move
                        self.random_move = True
                else:
                    self.eat = True
                    self.hungerCount = 0
            else:
                if self.mate_start < time_step and self.gender == 0:
                    #print "mating time"
                    if self.mate_cooldown <= 0  and self.altruist_mode == 0:
                        [self.nearest_mate, self.nearest_mate_dist] = self.findMate(animats, busy_grid)
                        if self.nearest_mate_dist == 1: #ask to mate
                            self.ask_mate = True
                        elif self.nearest_mate: #approach mate
                            self.approach_mate = True
                    else: 
                        #print "test"
                        [self.nearest_hungry, self.nearest_hungry_dist] = self.findHungry(animats, busy_grid)
                        if self.nearest_hungry:
                            if self.altruist_mode == 0:
                                x = self.nearest_hungry.numAlt - self.nearest_hungry.numCht
                                y = self.numAlt - self.numCht
                                help_prob = self.altruist_prob * (0.000064 * pow(x-alt_offset, 3) + 1)
                                help_prob = min(help_prob, self.altruist_prob * 2)
                                decision = random.random()
                                if decision < help_prob:
                                    if not self.holding_food:
                                        if food_under > 0:
                                            self.dig_food = True
                                            self.altruist_mode = 1
                                        else:
                                            self.random_move = True
                                    elif self.nearest_hungry_dist == 1:
                                        self.give_food = True
                                        #print "giving", self.gender, self.x, self.y, self.nearest_hungry.x, self.nearest_hungry.y
                                    else:
                                        #print "approach hungry", self.gender, self.x, self.y, self.nearest_hungry.x, self.nearest_hungry.y
                                        self.approach_hungry = True
                                else: self.random_move = True
                            else:
                                if self.nearest_hungry_dist == 1:
                                    self.give_food = True
                                    #print "giving", self.gender, self.x, self.y, self.nearest_hungry.x, self.nearest_hungry.y
                                else:
                                    #print "approach hungry", self.gender, self.x, self.y, self.nearest_hungry.x, self.nearest_hungry.y
                                    self.approach_hungry = True
                        else:
                            self.random_move = True
                else:
                    #if self.gender == 1:
                    #    [self.nearest_sick, self.nearest_sick_dist] = self.findSick(animats, busy_grid)
                    #    if self.nearest_sick:
                    #        if self.altruist_mode == 0:
                    #            x = self.nearest_sick.numAlt - self.nearest_sick.numCht
                    #            y = self.numAlt - self.numCht
                    #            help_prob = self.altruist_prob * (0.000064 * pow(x-alt_offset, 3) + 1) 
                    #            help_prob = min(help_prob, self.altruist_prob * 2)
                    #            decision = random.random()
                    #            if decision < help_prob:
                    #                if self.nearest_sick_dist == 1:
                    #                    self.heal = True
                    #                    #print "healing", self.gender, self.x, self.y, self.nearest_sick.x, self.nearest_sick.y
                    #                else:
                    #                    self.approach_sick = True
                    #            else: self.random_move = True
                    #        else:
                    #            if self.nearest_sick_dist == 1:
                    #                self.heal = True
                    #                #print "healing", self.gender, self.x, self.y, self.nearest_sick.x, self.nearest_sick.y
                    #            else: self.approach_sick = True
                    #    else:
                    #        self.random_move = True
                    #else:
                    [self.nearest_hungry, self.nearest_hungry_dist] = self.findHungry(animats, busy_grid)
                    if self.nearest_hungry:
                        if self.altruist_mode == 0:
                            x = self.nearest_hungry.numAlt - self.nearest_hungry.numCht
                            y = self.numAlt - self.numCht
                            help_prob = self.altruist_prob * (0.000064 * pow(x-alt_offset, 3) + 1)
                            help_prob = min(help_prob, self.altruist_prob * 2)
                            decision = random.random()
                            if decision < help_prob:
                                if not self.holding_food:
                                    if food_under > 0:
                                        self.dig_food = True
                                        self.altruist_mode = 1
                                    else:
                                        self.random_move = True
                                elif self.nearest_hungry_dist == 1:
                                    self.give_food = True
                                    #print "giving", self.gender, self.x, self.y, self.nearest_hungry.x, self.nearest_hungry.y
                                else:
                                    #print "approach hungry", self.gender, self.x, self.y, self.nearest_hungry.x, self.nearest_hungry.y
                                    self.approach_hungry = True
                            else: self.random_move = True
                        else:
                            if self.nearest_hungry_dist == 1:
                                self.give_food = True
                                #print "giving", self.gender, self.x, self.y, self.nearest_hungry.x, self.nearest_hungry.y
                            else:
                                #print "approach hungry", self.gender, self.x, self.y, self.nearest_hungry.x, self.nearest_hungry.y
                                self.approach_hungry = True
                    else:
                        self.random_move = True
    
    
    def findMate(self, animats, busy_grid):
        baseX = self.x #set base coordinate to be the animat's location
        baseY = self.y
        baseD = self.direction #get the direction to determine what the animat can see
        closest_dist = 1000
        chosen = None
        decision = random.random()
        for a in animats:
            aniX = a.x #get coordinates
            aniY = a.y
            ani_dist = -1
            if a.generation == self.generation and a.gender == 1 and a.child == None and not busy_grid[aniY][aniX] and a.fitness > 0 and a.fitness >= 750:
            #if a.generation == self.generation and a.gender != self.gender and a.child == None and a.age > 150:
                if baseD == 0 and aniY <= baseY: #if facing north and target animat is further north
                    ani_distX = baseX - aniX
                    ani_distY = baseY - aniY
                    ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
                if baseD == 1 and aniX >= baseX: #if facing east and target animat is further east
                    ani_distX = baseX - aniX
                    ani_distY = baseY - aniY
                    ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
                if baseD == 2 and aniY >= baseY: #if facing south and target animat is futher south
                    ani_distX = baseX - aniX
                    ani_distY = baseY - aniY
                    ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
                if baseD == 3 and aniX <= baseX: #if facing west and target animat is further west
                    ani_distX = baseX - aniX
                    ani_distY = baseY - aniY
                    ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
                if ani_dist > 0 and ani_dist <= 5: #if within visual range (and not itself)
                    x = a.numAlt - a.numCht
                    #y = self.numAlt - self.numCht
                    mate_prob = (math.erf(float(x) / 20) + 1) / 2
                    #mate_prob = (0.0005 * pow(x, 3) + 0.5)
                    #mate_prob -= self.altruist_prob
                    #mate_prob += 0.5
                    #mate_prob = 0.5
                    if ani_dist < closest_dist and decision < mate_prob: #if this animat is the closest so far, set it as the closest
                        closest_dist = ani_dist
                        chosen = a
        return [chosen, closest_dist] #return chosen animat and the distance
    
    def findHungry(self, animats, busy_grid):
        baseX = self.x #set base coordinate to be the animat's location
        baseY = self.y
        baseD = self.direction #get the direction to determine what the animat can see
        closest_dist = 1000
        chosen = None
        for a in animats:
            aniX = a.x #get coordinates
            aniY = a.y
            ani_dist = -1
            #if a.gender == 1 and a.fitness < 750 and not busy_grid[aniY][aniX] and a.fitness > 0:
            if a.fitness < 750 and not busy_grid[aniY][aniX] and a.fitness > 0:
            #if a.generation == self.generation and a.gender != self.gender and a.child == None and a.age > 150:
                if baseD == 0 and aniY <= baseY: #if facing north and target animat is further north
                    ani_distX = baseX - aniX
                    ani_distY = baseY - aniY
                    ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
                if baseD == 1 and aniX >= baseX: #if facing east and target animat is further east
                    ani_distX = baseX - aniX
                    ani_distY = baseY - aniY
                    ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
                if baseD == 2 and aniY >= baseY: #if facing south and target animat is futher south
                    ani_distX = baseX - aniX
                    ani_distY = baseY - aniY
                    ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
                if baseD == 3 and aniX <= baseX: #if facing west and target animat is further west
                    ani_distX = baseX - aniX
                    ani_distY = baseY - aniY
                    ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
                if ani_dist > 0 and ani_dist <= 5: #if within visual range (and not itself)
                    if ani_dist < closest_dist: #if this animat is the closest so far, set it as the closest
                        closest_dist = ani_dist
                        chosen = a
        return [chosen, closest_dist] #return chosen animat and the distance
    
    #def findSick(self, animats, busy_grid):
    #    baseX = self.x #set base coordinate to be the animat's location
    #    baseY = self.y
    #    baseD = self.direction #get the direction to determine what the animat can see
    #    closest_dist = 1000
    #    chosen = None
    #    for a in animats:
    #        aniX = a.x #get coordinates
    #        aniY = a.y
    #        ani_dist = -1
    #        if a.gender == 0 and a.sick and not busy_grid[aniY][aniX] and a.fitness > 0:
    #        #if a.generation == self.generation and a.gender != self.gender and a.child == None and a.age > 150:
    #            if baseD == 0 and aniY <= baseY: #if facing north and target animat is further north
    #                ani_distX = baseX - aniX
    #                ani_distY = baseY - aniY
    #                ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
    #            if baseD == 1 and aniX >= baseX: #if facing east and target animat is further east
    #                ani_distX = baseX - aniX
    #                ani_distY = baseY - aniY
    #                ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
    #            if baseD == 2 and aniY >= baseY: #if facing south and target animat is futher south
    #                ani_distX = baseX - aniX
    #                ani_distY = baseY - aniY
    #                ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
    #            if baseD == 3 and aniX <= baseX: #if facing west and target animat is further west
    #                ani_distX = baseX - aniX
    #                ani_distY = baseY - aniY
    #                ani_dist = math.sqrt(pow(ani_distX, 2) + pow(ani_distY, 2))
    #            if ani_dist > 0 and ani_dist <= 5: #if within visual range (and not itself)
    #                if ani_dist < closest_dist: #if this animat is the closest so far, set it as the closest
    #                    closest_dist = ani_dist
    #                    chosen = a
    #    return [chosen, closest_dist] #return chosen animat and the distance