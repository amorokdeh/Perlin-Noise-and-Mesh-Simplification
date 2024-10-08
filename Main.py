import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PerlinNoise import *
from MeshSimplification import *
import time

pygame.init()
width, height = 800, 600
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
gluPerspective(45, (width / height), 0.1, 50.0)
glTranslatef(0.0, 0.0, -5)

class Text:
    def __init__(self, text, function, x, y, size, color, hover_color):
        self.text = text
        self.function = function
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.hover_color = hover_color
        self.clicked = False

    def render(self, is_hover):
        font = pygame.font.Font(None, self.size)
        if is_hover:
            text_surface = font.render(self.text, True, self.hover_color, (0, 0, 0))
        else:
            text_surface = font.render(self.text, True, self.color, (0, 0, 0))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        glLoadIdentity()
        glRasterPos3f(self.x, self.y, -1.0)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

white = 255, 255, 255
yellow = 255, 255, 0

def runMenu():
    #change menu
    global currentMenu
    if selected == "Main menu" or selected == "Perlin Noise" or selected == "Mesh Simplification":
        currentMenu = selected
    #select menu
    if currentMenu == "Main menu":
        mainMenu()
        return
    elif currentMenu == "Perlin Noise":
        PerlinNoiseMenu()
        return
    elif currentMenu == "Mesh Simplification":
        MeshSimplificationMenu()
        return

def mainMenu():
    global currentMenu
    global texts
    #change texts
    texts = [
        Text("Perlin Noise", "Perlin Noise", -0.9, 0.2, 32, white, yellow),
        Text("Mesh Simplification", "Mesh Simplification", -0.9, 0, 32, white, yellow),
        Text("Exit", "Exit",-0.9, -0.2, 32, white, yellow),
    ]
    #select
    if selected == "Perlin Noise":
        currentMenu = "Perlin Noise"
        return
    elif selected == "Mesh Simplification":
        currentMenu = "Mesh Simplification"
        return
    elif selected == "Exit":
        pygame.quit()
        quit()
        return

def PerlinNoiseMenu():
    global currentMenu, texts, meshWidth, meshHeight, freq, amplitude
    #change texts
    texts = [
        Text(("Width: " + str(int (meshWidth))), "",-0.9, 0.2, 32, white, white), Text(" + ", "width up", -0.4, 0.2, 32, white, yellow), Text(" - ", "width down", -0.3, 0.2, 32, white, yellow),
        Text(("Height: " + str(int (meshHeight))), "", -0.9, 0, 32, white, white), Text(" + ", "height up",-0.4, 0, 32, white, yellow), Text(" - ", "height down",-0.3, 0, 32, white, yellow),
        Text(("Frequency: " + str(float ("%.2f" % freq))), "", -0.9, -0.2, 32, white, white), Text(" + ", "freq up",-0.4, -0.2, 32, white, yellow), Text(" - ", "freq down", -0.3, -0.2, 32, white, yellow),
        Text(("Amplitude: " + str(float ("%.2f" % amplitude))), "", -0.9, -0.4, 32, white, white), Text(" + ", "amplitude up", -0.4, -0.4, 32, white, yellow), Text(" - ", "amplitude down", -0.3, -0.4, 32, white, yellow),
        Text("Run", "Run", -0.9, -0.7, 32, white, yellow), Text("Back", "Back", 0.7, -0.7, 32, white, yellow),
    ]
    #select
    if selected == "Back":
        currentMenu = "Main menu"
        return
    elif selected == "Run":
        currentMenu = "Main menu"
        generate_terrain(meshWidth, meshHeight, freq, amplitude)
        runPerlinNoise()
        return
    
    elif selected == "width up":
        meshWidth = meshWidth + 1
    elif selected == "width down":
        meshWidth = meshWidth - 1

    elif selected == "height up":
        meshHeight = meshHeight + 1
    elif selected == "height down":
        meshHeight = meshHeight - 1

    elif selected == "freq up":
        freq = freq + 0.1
    elif selected == "freq down":
        freq = freq - 0.1

    elif selected == "amplitude up":
        amplitude = amplitude + 0.1
    elif selected == "amplitude down":
        amplitude = amplitude - 0.1

def MeshSimplificationMenu():
    global currentMenu, texts, target_faces
    #change texts
    texts = [
        Text(("Target faces: " + str(int (target_faces))), "",-0.9, 0.2, 32, white, white), Text(" + ", "target_faces up", -0.4, 0.2, 32, white, yellow), Text(" - ", "target_faces down", -0.3, 0.2, 32, white, yellow),
        Text("Run", "Run", -0.9, -0.7, 32, white, yellow), Text("Back", "Back", 0.7, -0.7, 32, white, yellow),
    ]
    #select
    if selected == "Back":
        currentMenu = "Main menu"
        return
    elif selected == "Run":
        currentMenu = "Main menu"
        obj_file = 'terrain.obj'
        vertices, faces = load_obj(obj_file)
        simplified_vertices, simplified_faces = simplify_mesh(vertices, faces, target_faces)
        export_obj('Simplified '+ obj_file, simplified_vertices, simplified_faces)
        visualize_mesh(simplified_vertices, simplified_faces)
        return
    elif selected == "target_faces up":
        target_faces = target_faces + 10
    elif selected == "target_faces down":
        target_faces = target_faces - 10

def ControlRun():
    #variables for menus
    global currentMenu
    global selected
    global texts
    currentMenu = "Main menu"
    selected = "Main menu"
    texts = [
    Text("Perlin Noise", "Perlin Noise", -0.9, 0.2, 32, white, yellow),
    Text("Mesh Simplification", "Mesh Simplification", -0.9, 0, 32, white, yellow),
    Text("Exit", "Exit",-0.9, -0.2, 32, white, yellow),
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #Text
        mouse_x, mouse_y = pygame.mouse.get_pos()
        normalized_mouse_x = (mouse_x / width) * 2 - 1
        normalized_mouse_y = -((mouse_y / height) * 2 - 1)
        for text in texts:
            font = pygame.font.Font(None, text.size)
            text_surface = font.render(text.text, True, (255, 255, 255), (0, 0, 0))
            text_width = text_surface.get_width() / width * 2
            text_height = text_surface.get_height() / height * 2
            is_hover = (normalized_mouse_x > text.x and normalized_mouse_x < text.x + text_width and
                        normalized_mouse_y > text.y and normalized_mouse_y < text.y + text_height)
            text.render(is_hover)

            #Clicked
            if(is_hover and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and text.clicked == False):
                    text.clicked = True
                    selected = text.function
                    print(selected)

            if(event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                text.clicked = False

            runMenu()
            selected = ""
            time.sleep(0.005)

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    ControlRun()