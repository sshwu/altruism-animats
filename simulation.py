import environment

class Simulation:
    def __init__(self, num_animats, width, height, generations, learning_mode, food_spawn):
        self.environment = environment.Environment(num_animats, width, height, food_spawn, learning_mode)
        self.generations = generations
        #self.learning = learning_mode
        #self.spawn_rate = food_spawn
    
    def run(self):
        x = 0
        f1 = open('./Logs/Final/emergencytest.txt', 'w+')
        while self.environment.oldest_gen < self.generations and len(self.environment.animats) > 0:
            if len(self.environment.animats) > 0 and x % 5000 == 0: print x, "\t", len(self.environment.animats)
            self.environment.update(x)
            x += 1
        for i in range(self.generations):
            if self.environment.gen_pop[2][i] > 0:
                avg_altm = self.environment.tot_alt[0][i] / self.environment.gen_pop[0][i]
                avg_altf = self.environment.tot_alt[1][i] / self.environment.gen_pop[1][i]
                avg_alt = self.environment.tot_alt[2][i] / self.environment.gen_pop[2][i]
                #avg_endalt = self.environment.tot_endalt[i] / self.environment.gen_pop[i]
                avg_chtm = float(self.environment.tot_cht[0][i]) / self.environment.gen_pop[0][i]
                avg_chtf = float(self.environment.tot_cht[1][i]) / self.environment.gen_pop[1][i]
                avg_cht = float(self.environment.tot_cht[2][i]) / self.environment.gen_pop[2][i]
                avg_altrecm = float(self.environment.tot_altrec[0][i]) / (self.environment.gen_pop[0][i] * 2)
                avg_altrecf = float(self.environment.tot_altrec[1][i]) / (self.environment.gen_pop[1][i] * 2)
                avg_altrec = float(self.environment.tot_altrec[2][i]) / (self.environment.gen_pop[2][i] * 2)
                #pun = float(self.environment.tot_pun[i]) / self.environment.gen_pop[i]
                print >>f1, i, self.environment.gen_pop[0][i], self.environment.gen_pop[1][i], "\t", avg_alt, "\t", avg_altm, "\t", avg_altf, "\t", avg_altrec, "\t", avg_altrecm, "\t", avg_altrecf, "\t", avg_cht, "\t", avg_chtm, "\t", avg_chtf
                #print >>f1, i, self.environment.gen_pop[1][i], "\t", avg10, "\t", pun1#, "\t", fit1
        #print >>f1, "alt distribution"
        #for j in range(self.generations / 10 + 1):
        #    for j1 in range(20):
        #        print >>f1, self.environment.pop_dist[j][j1], "\t",
        #    print >>f1
        #print >>f1, "end distribution"
        #for k in range(self.generations / 10 + 1):
        #    for k1 in range(20):
        #        print >>f1, self.environment.end_dist[k][k1], "\t",
        #    print >>f1
        #print >>f1, "acc distribution"
        #for l in range(self.generations / 10 + 1):
        #    for l1 in range(20):
        #        print >>f1, self.environment.acc_dist[l][l1], "\t",
        #    print >>f1
        #print >>f1, "rej distribution"
        #for m in range(self.generations / 10 + 1):
        #    for m1 in range(20):
        #        print >>f1, self.environment.rej_dist[m][m1], "\t",
        #    print >>f1
        print >>f1, "data"
        for g in range(2):
            print >>f1, "gender", g
            for n in range(self.generations / 10 + 1):
                print >>f1, n, "set"
                for p in range(len(self.environment.dat_dist[g][n])):
                    for q in range(len(self.environment.dat_dist[g][n][p])):
                        print >>f1, self.environment.dat_dist[g][n][p][q], "\t",
                    print >>f1
        f1.close()
        
if __name__ == "__main__":
    simulation = Simulation(200, 40, 40, 1, 0, 40) #creates the simulation
    simulation.run()