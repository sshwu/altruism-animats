import numpy
from numpy import random
import animat
import copy

class Environment:
    def __init__(self, init_pop, width, height, food_spawn, learning_mode):
        self.mating_req = 0
        self.mating_acc = 0
        self.learning = learning_mode
        self.spawn = food_spawn
        self.gen_pop = [[0 for x in range(55)] for x0 in range(3)]
        self.tot_alt = [[0 for y in range(55)] for y0 in range(3)]
        #self.tot_rec = [0 for y in range(55)]
        self.pop_dist = [[[0 for z0 in range(20)] for z in range(11)] for z1 in range(3)]
        self.end_dist = [[0 for z0 in range(20)] for z in range(11)]
        self.acc_dist = [[0 for z0 in range(20)] for z in range(11)]
        self.rej_dist = [[0 for z0 in range(20)] for z in range(11)]
        self.dat_dist = [[[] for z in range(11)] for z0 in range(2)]
        self.tot_altrec = [[0 for x in range(55)] for x0 in range(3)]
        self.tot_cht = [[0 for x in range(55)] for x0 in range(3)]
        self.tot_endalt = [0 for x in range(55)]
        #self.mate_dist = [[[0 for z0 in range(20)] for z in range(11)] for z1 in range(2)]
        #self.tot_fit = [[0 for x in range(55)] for x1 in range(2)]
        self.tot_pun = [0 for y in range(55)]
        self.width = width #width of the environment (x size)
        self.height = height #height of the environment (y size)
        self.num_animats = init_pop #number of animats to start with
        self.animats = [] #list of animats
        self.new_animats = [] #list of new animats to be added to main animats list
        self.dead_animats = [] #list of dead animats to be removed from main animats list
        self.giving_grid = [[None for col in range(width)] for row in range(height)]
        self.asking_grid = [[None for col in range(width)] for row in range(height)] #grid with chromosomes from those who asked to mate
        self.healing_grid = [[None for col in range(width)] for row in range(height)] #contains coordinates of the healer
        self.protect_grid = [[False for col in range(width)] for row in range(height)]
        self.cheat_grid = [[None for col in range(width)] for row in range(height)]
        self.punish_grid = [[False for col in range(width)] for row in range(height)]
        self.animat_grid = [[0 for col in range(width)] for row in range(height)] #grid showing locations of the animats
        self.busy_grid = [[False for col in range(width)] for row in range(height)]
        self.reject_grid = [[False for col in range(width)] for row in range(height)]
        self.oldest_gen = 0
        while len(self.animats) < self.num_animats:
            posX = random.randint(0, width) #initial position
            posY = random.randint(0, height)
            done = False
            alt_prob = (random.random()/2) + 0.5
            #if alt_prob < 0: alt_prob = 0.0001
            #if alt_prob >= 1: alt_prob = 0.9999
            while not done: #check to make sure each location only has one animat
                if self.animat_grid[posY][posX] == 0: #if location is empty
                    self.animat_grid[posY][posX] = 1 #put animat in chosen spot
                    done = True
                else: #otherwise retry
                    posX = random.randint(0, width)
                    posY = random.randint(0, height)
            a_male = animat.Animat(posX, posY, 0, alt_prob, 0, self.gen_pop, self.tot_alt, self.pop_dist, 1, self.tot_pun) #make new animat
            self.animats.append(a_male) #add to list of animats
            posX = random.randint(0, width) #same for females as males
            posY = random.randint(0, height)
            done = False
            alt_prob = (random.random()/2) + 0.5
            while not done:
                if self.animat_grid[posY][posX] == 0:
                    self.animat_grid[posY][posX] = 1
                    done = True
                else:
                    posX = random.randint(0, width)
                    posY = random.randint(0, height)
            a_female = animat.Animat(posX, posY, 1, alt_prob, 0, self.gen_pop, self.tot_alt, self.pop_dist, 1, self.tot_pun)
            self.animats.append(a_female)
            
        self.food_grid = [[0 for col in range(width)] for row in range(height)] #grid showing where food is
        for h in range(height):
            for w in range(width):
                self.food_grid[h][w] = random.randint(0,self.spawn) - (self.spawn - 1)
        
    def update(self, time_step):
        #print len(self.animats)
        for w in range(self.width): #going through each spot
            for r in range(self.height):
                if self.food_grid[r][w] < 0: #if there isn't already food there
                    self.food_grid[r][w] += 1
                elif self.food_grid[r][w] == 0:
                    self.food_grid[r][w] = 50
        #print len(self.foods)
        new_oldest_gen = 50
        self.animat_grid = [[0 for col in range(self.width)] for row in range(self.height)]
        for a in self.animats:
            if a.fitness <= 0 or time_step >= (a.generation + 1) * 5000:
                #print "died", a.gender, a.numAlt, a.numCht#, "\t", a.x, a.y
                #self.tot_fit[a.gender][a.generation] += a.total_fitness
                self.tot_cht[a.gender][a.generation] += a.numCht
                self.tot_cht[2][a.generation] += a.numCht
                self.tot_altrec[a.gender][a.generation] += a.numAlt
                self.tot_altrec[2][a.generation] += a.numAlt
                self.tot_endalt[a.generation] += a.altruist_prob
                if a.generation < 50 and (a.generation == 0 or a.generation % 10 == 9):
                    dist_index = int(numpy.floor(a.altruist_prob * 20))
                    if dist_index < 0: dist_index = 0
                    if dist_index > 19: dist_index = 19
                    if a.generation == 0:
                        self.acc_dist[0][dist_index] += a.numAccepted
                        self.rej_dist[0][dist_index] += a.numRejected
                        self.end_dist[0][dist_index] += 1
                        self.dat_dist[a.gender][0].append([a.altruist_prob, a.altruist_prob - a.orig_prob, a.numChildren, a.numAlt, a.numCht])
                    else:
                        self.acc_dist[(a.generation+1)/10][dist_index] += a.numAccepted
                        self.rej_dist[(a.generation+1)/10][dist_index] += a.numRejected
                        self.end_dist[(a.generation+1)/10][dist_index] += 1
                        self.dat_dist[a.gender][(a.generation+1)/10].append([a.altruist_prob, a.altruist_prob - a.orig_prob, a.numChildren, a.numAlt, a.numCht])
                #if self.healing_grid[a.y][a.x]:
                #    healer_coord = self.healing_grid[a.y][a.x]
                #    if a.expect_recip: self.giving_grid[healer_coord[1]][healer_coord[0]] = [a.x, a.y]
                #    self.healing_grid[a.y][a.x] = None
                elif self.giving_grid[a.y][a.x]:
                    #giver_coord = self.giving_grid[a.y][a.x]
                    #self.protect_grid[giver_coord[1]][giver_coord[0]] = [a.x, a.y]
                    self.giving_grid[a.y][a.x] = None
                if a.gender == 1 and a.child:
                    new_ani = copy.deepcopy(a.child)
                    posX = random.randint(0, self.width)
                    posY = random.randint(0, self.height)
                    done = False
                    while not done:
                        if self.animat_grid[posY][posX] == 0:
                            self.animat_grid[posY][posX] = 1
                            done = True
                        else:
                            posX = random.randint(0, self.width)
                            posY = random.randint(0, self.height)
                    new_ani.x = posX #give the new animat its coordinates
                    new_ani.y = posY
                    self.new_animats.append(new_ani)
                self.animat_grid[a.y][a.x] = 0
                self.dead_animats.append(a)
            else:
                self.animat_grid[a.y][a.x] = 1
        if self.dead_animats:
            for dead_ani in self.dead_animats:
                self.animats.remove(dead_ani)
            self.dead_animats = []
        for ani in self.animats: #update each animat
            if ani.generation < new_oldest_gen: new_oldest_gen = ani.generation
            if len(self.animats) > 400 and ani.generation == self.oldest_gen:
                ani.fitness -= 25
            #if ani.numCht > ani.numAlt:
            #    ani.fitness -= (ani.numCht - ani.numAlt) / 10
            ani.nearest_mate = None #initial values
            ani.nearest_mate_dist = -1
            ani.nearest_food_dist = -1
            ani.update(self.asking_grid, self.giving_grid, self.healing_grid, self.protect_grid, self.food_grid[ani.y][ani.x], self.punish_grid, self.busy_grid, self.animats, self.gen_pop, self.tot_alt, time_step, self.cheat_grid, self.learning, self.reject_grid) #update the animat
            if not ani.dead and ani.child: #if the child has grown up, release it into the environment
                if ani.child.age >= 250:
                    new_ani = copy.deepcopy(ani.child) #create copy of the child
                    posX = random.randint(0, self.width)
                    posY = random.randint(0, self.height)
                    done = False
                    while not done:
                        if self.animat_grid[posY][posX] == 0:
                            self.animat_grid[posY][posX] = 1
                            done = True
                        else:
                            posX = random.randint(0, self.width)
                            posY = random.randint(0, self.height)
                    new_ani.x = posX #give the new animat its coordinates
                    new_ani.y = posY
                    new_ani.direction = random.randint(0,4) #give the new animat a direction
                    self.new_animats.append(new_ani) #add to list of new animats, to be added to li
                    ani.child = None #no child for the mother
            if ani.punished:
                #print ani.x, ani.y, "got punished"
                self.punish_grid[ani.y][ani.x] = False
                self.busy_grid[ani.y][ani.x] = False
            elif ani.mate:
                gender = random.randint(0,2)
                #avg_alt = (ani.asked[0] + ani.altruist_prob) / 2.0
                #avg_rec = (ani.asked[1] + ani.reciproc_prob) / 2.0
                if gender == 0:
                    avg_alt = (4 * ani.asked[0] + ani.altruist_prob) / 5.0
                    #avg_rec = (3 * ani.asked[1] + ani.reciproc_prob) / 4.0
                else:
                    avg_alt = (ani.asked[0] + ani.altruist_prob * 4) / 5.0
                    #avg_rec = (ani.asked[1] + ani.reciproc_prob * 3) / 4.0
                #r = random.random()
                #if r < 0.05:
                #    alt_prob = ((random.random() * 0.2) - 0.1) + avg_alt
                #    #rec_prob = ((random.random() * 0.2) - 0.1) + avg_rec
                #else:
                #    alt_prob = avg_alt
                #    #rec_prob = avg_rec
                alt_prob = random.normal(avg_alt, 0.02)
                #rec_prob = random.normal(avg_rec, 0.01)
                if alt_prob < 0: alt_prob = 0
                if alt_prob >= 1: alt_prob = 0.9999
                ani.child = animat.Animat(ani.x, ani.y, gender, alt_prob, ani.generation + 1, self.gen_pop, self.tot_alt, self.pop_dist, ani.punish_gene, self.tot_pun)
                ani.mate = False
                self.asking_grid[ani.y][ani.x] = None
                self.busy_grid[ani.y][ani.x] = False
            elif ani.ask_mate: #male setting asking_grid after asking female to mate
                #print "asking", ani.altruist_prob, ani.reciproc_prob, ani.numCht, ani.numAlt
                self.asking_grid[ani.nearest_mate.y][ani.nearest_mate.x] = [ani.altruist_prob, ani.numCht, ani.numAlt, ani.x, ani.y]
                self.busy_grid[ani.nearest_mate.y][ani.nearest_mate.x] = True
                ani.ask_mate = False
                ani.expect_mate = True
                ani.mate_cooldown = 5
            elif ani.heal: #either initiate or reciprocate
                if ani.reciprocate:
                    ani.fitness -= 15
                    self.healing_grid[ani.given[1]][ani.given[0]] = [ani.x, ani.y]
                    self.busy_grid[ani.y][ani.x] = False
                    self.giving_grid[ani.y][ani.x] = None
                    ani.reciprocate = False
                    ani.numAlt += 1
            #    else:
            #        ani.fitness -= 30
            #        self.healing_grid[ani.nearest_sick.y][ani.nearest_sick.x] = [ani.x, ani.y]
            #        ani.expect_recip = True
            #        self.busy_grid[ani.y][ani.x] = True
            #        self.busy_grid[ani.nearest_sick.y][ani.nearest_sick.x] = True
            #        ani.altruist_mode = 0
            #    ani.heal = False
            elif ani.give_food: #initiate only
                ani.food -= 50
                self.giving_grid[ani.nearest_hungry.y][ani.nearest_hungry.x] = [ani.x, ani.y]
                ani.expect_recip = True
                self.busy_grid[ani.y][ani.x] = True
                self.busy_grid[ani.nearest_hungry.y][ani.nearest_hungry.x] = True
                ani.altruist_mode = 0
                ani.give_food = False
            #elif ani.protect: #reciprocate only
            #    ani.fitness -= 30
            #    ani.numAlt += 1
            #    self.protect_grid[ani.healed[1]][ani.healed[0]] = True
            #    self.busy_grid[ani.y][ani.x] = False
            #    self.busy_grid[ani.healed[1]][ani.healed[0]] = True
            #    self.healing_grid[ani.y][ani.x] = None
            #    ani.protect = False
            elif ani.punish:
                #r = random.random()
                self.busy_grid[ani.y][ani.x] = False
                #if ani.punish_gene == 1:#r < ani.altruist_prob * 2:
                self.punish_grid[ani.cheated[1]][ani.cheated[0]] = True
                self.busy_grid[ani.cheated[1]][ani.cheated[0]] = True
                #else: self.busy_grid[ani.cheated[1]][ani.cheated[0]] = False
                self.cheat_grid[ani.y][ani.x] = None
                #ani.fitness -= 5
                ani.expect_recip = False
                ani.punish = False
            elif ani.cheat:
                #if ani.gender == 0 and ani.healed:
                #    self.cheat_grid[ani.healed[1]][ani.healed[0]] = [ani.x, ani.y]
                #    self.healing_grid[ani.y][ani.x] = None
                #elif ani.gender == 1 and ani.given:
                if ani.given:
                    self.cheat_grid[ani.given[1]][ani.given[0]] = [ani.x, ani.y]
                    self.giving_grid[ani.y][ani.x] = None
                ani.cheat = False
            elif ani.dig_food:
                #if ani.gender == 0:
                ani.food += self.food_grid[ani.y][ani.x]
                self.food_grid[ani.y][ani.x] = 0
                ani.fitness -= 15
                if ani.gender == 1:
                    ani.fitness -= 10
                #else:
                #    ani.food += self.food_grid[ani.y][ani.x]
                #    self.food_grid[ani.y][ani.x] = 0
                #    ani.fitness -= 40
                if self.food_grid[ani.y][ani.x] == 0: self.food_grid[ani.y][ani.x] = 1 - self.spawn
                r = random.random()
                #if ani.gender == 0 and r < 0.25: #TWEAK THIS
                #    ani.sick = True
                #elif ani.gender == 1 and r < 0.05: #TWEAK THIS
                #    if ani.immunities == 0: ani.fitness -= 100
                #    else: ani.immunities -= 1
                ani.dig_food = False
            elif ani.eat:
                #print "eat", ani.gender, ani.food
                if ani.gender == 0 or ani.child == None:
                    ani.fitness += ani.food
                else:
                    ani.fitness += ani.food/2
                    ani.child.fitness += ani.food/2
                ani.food = 0
                ani.eat = False
                ani.altruist_mode = 0
            elif ani.approach_mate:
                distX = ani.x - ani.nearest_mate.x
                distY = ani.y - ani.nearest_mate.y
                if distX != 0: stepX = distX / abs(distX)
                else: stepX = 0
                if distY != 0: stepY = distY / abs(distY)
                else: stepY = 0
                newX = ani.x + stepX
                newY = ani.y + stepY
                if abs(distY) > abs(distX):
                    if newY >= 0 and newY < self.height and self.animat_grid[newY][ani.x] == 0:
                        self.animat_grid[newY][ani.x] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.y += stepY
                        ani.direction = stepY + 1
                        ani.fitness -= 4
                    elif newX >= 0 and newX < self.width and self.animat_grid[ani.y][newX] == 0:
                        self.animat_grid[ani.y][newX] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.x += stepX
                        ani.direction = stepX * -1 + 2
                        ani.fitness -= 4
                else:
                    if newX >= 0 and newX < self.width and self.animat_grid[ani.y][newX] == 0:
                        self.animat_grid[ani.y][newX] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.x += stepX
                        ani.direction = stepX * -1 + 2
                        ani.fitness -= 4
                    elif newY >= 0 and newY < self.height and self.animat_grid[newY][ani.x] == 0:
                        self.animat_grid[newY][ani.x] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.y += stepY
                        ani.direction = stepY + 1
                        ani.fitness -= 4
                ani.fitness -= 1
                ani.approach_mate = False
                ani.altruist_mode = 0
            #elif ani.approach_sick:
            #    distX = ani.x - ani.nearest_sick.x
            #    distY = ani.y - ani.nearest_sick.y
            #    if distX != 0: stepX = distX / abs(distX)
            #    else: stepX = 0
            #    if distY != 0: stepY = distY / abs(distY)
            #    else: stepY = 0
            #    newX = ani.x + stepX
            #    newY = ani.y + stepY
            #    if abs(distY) > abs(distX):
            #        if newY >= 0 and newY < self.height and self.animat_grid[newY][ani.x] == 0:
            #            self.animat_grid[newY][ani.x] = 1
            #            self.animat_grid[ani.y][ani.x] = 0
            #            ani.y += stepY
            #            ani.direction = stepY + 1
            #            ani.fitness -= 4
            #        elif newX >= 0 and newX < self.width and self.animat_grid[ani.y][newX] == 0:
            #            self.animat_grid[ani.y][newX] = 1
            #            self.animat_grid[ani.y][ani.x] = 0
            #            ani.x += stepX
            #            ani.direction = stepX * -1 + 2
            #            ani.fitness -= 4
            #    else:
            #        if newX >= 0 and newX < self.width and self.animat_grid[ani.y][newX] == 0:
            #            self.animat_grid[ani.y][newX] = 1
            #            self.animat_grid[ani.y][ani.x] = 0
            #            ani.x += stepX
            #            ani.direction = stepX * -1 + 2
            #            ani.fitness -= 4
            #        elif newY >= 0 and newY < self.height and self.animat_grid[newY][ani.x] == 0:
            #            self.animat_grid[newY][ani.x] = 1
            #            self.animat_grid[ani.y][ani.x] = 0
            #            ani.y += stepY
            #            ani.direction = stepY + 1
            #            ani.fitness -= 4
            #    ani.fitness -= 1
            #    ani.approach_sick = False
            #    ani.altruist_mode = 1
            elif ani.approach_hungry:
                #print "actual", ani.gender, ani.x, ani.y, ani.nearest_hungry.x, ani.nearest_hungry.y
                distX = ani.x - ani.nearest_hungry.x
                distY = ani.y - ani.nearest_hungry.y
                if distX != 0: stepX = distX / abs(distX)
                else: stepX = 0
                if distY != 0: stepY = distY / abs(distY)
                else: stepY = 0
                newX = ani.x + stepX
                newY = ani.y + stepY
                if abs(distY) > abs(distX):
                    if newY >= 0 and newY < self.height and self.animat_grid[newY][ani.x] == 0:
                        self.animat_grid[newY][ani.x] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.y += stepY
                        ani.direction = stepY + 1
                        ani.fitness -= 4
                    elif newX >= 0 and newX < self.width and self.animat_grid[ani.y][newX] == 0:
                        self.animat_grid[ani.y][newX] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.x += stepX
                        ani.direction = stepX * -1 + 2
                        ani.fitness -= 4
                else:
                    if newX >= 0 and newX < self.width and self.animat_grid[ani.y][newX] == 0:
                        self.animat_grid[ani.y][newX] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.x += stepX
                        ani.direction = stepX * -1 + 2
                        ani.fitness -= 4
                    elif newY >= 0 and newY < self.height and self.animat_grid[newY][ani.x] == 0:
                        self.animat_grid[newY][ani.x] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.y += stepY
                        ani.direction = stepY + 1
                        ani.fitness -= 4
                ani.fitness -= 1
                ani.approach_hungry = False
                ani.altruist_mode = 1
            elif ani.random_move:
                ani.altruist_mode = 0
                #print "random move"
                done = False
                while not done:
                    move = random.randint(0,4)
                    #ani.direction = move
                    if move == 0 and ani.y > 0 and self.animat_grid[ani.y - 1][ani.x] == 0:
                        self.animat_grid[ani.y - 1][ani.x] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.y -= 1
                        ani.direction = 0
                        ani.fitness -= 5
                        done = True
                        if ani.child:
                            ani.child.y -= 1
                            ani.child.fitness -= 4
                    elif move == 1 and ani.x < self.width - 1 and self.animat_grid[ani.y][ani.x + 1] == 0:
                        self.animat_grid[ani.y][ani.x + 1] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.x += 1
                        ani.direction = 1
                        ani.fitness -= 5
                        done = True
                        if ani.child:
                            ani.child.y -= 1
                            ani.child.fitness -= 4
                    elif move == 2 and ani.y < self.height - 1 and self.animat_grid[ani.y + 1][ani.x] == 0:
                        self.animat_grid[ani.y + 1][ani.x] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.y += 1
                        ani.direction = 2
                        ani.fitness -= 5
                        done = True
                        if ani.child:
                            ani.child.y -= 1
                            ani.child.fitness -= 4
                    elif move == 3 and ani.x > 0 and self.animat_grid[ani.y][ani.x - 1] == 0:
                        self.animat_grid[ani.y][ani.x - 1] = 1
                        self.animat_grid[ani.y][ani.x] = 0
                        ani.x -= 1
                        ani.direction = 3
                        ani.fitness -= 5
                        done = True
                        if ani.child:
                            ani.child.y -= 1
                            ani.child.fitness -= 4
                    done = True
                ani.random_move = False
            
        self.oldest_gen = new_oldest_gen
        if self.new_animats:
            for new_ani in self.new_animats:
                n = copy.deepcopy(new_ani)
                self.animats.append(n)
            self.new_animats = []
