import pygame
import os


import lib.utilities


#init 
pygame.init()
screen = pygame.display.set_mode(0,0)
clock = pygame.time.Clock()
running = True







#main function
def main():
    config=load_config() #load config
            
         
    
    pygame.quit()










if __name__ == '__main__' :
    main()