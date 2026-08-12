from manim import *

class DigestiveSystem(Scene):
    def construct(self):
        stomach = Circle(radius=1.5, color=BLUE, fill_opacity=0.5)
        esoph = Rectangle(height=0.5, width=1, color=RED, fill_opacity=0.5)
        esoph.next_to(stomach, UP)
        intest = VMobject()
        intest.set_points_as_corners([
            [0, 0, 0],
            [1, -1, 0],
            [2, 1, 0],
            [3, -1, 0],
            [4, 0, 0]
        ])
        intest.stretch(2, 0)
        intest.stretch(0.5, 1)
        intest.set_color(GREEN)
        intest.next_to(stomach, DOWN + RIGHT, buff=0)
        
        self.play(Create(esoph), Create(stomach), Create(intest))
        self.wait(1)
        
        dot = Dot(color=YELLOW)
        self.play(FadeIn(dot))
        
        self.play(dot.animate.move_to(esoph.get_bottom()))
        self.play(dot.animate.move_to(stomach.get_top()))
        self.play(dot.animate.move_to(intest.get_top()))
        self.play(dot.animate.move_to(intest.get_end()))
        self.wait(1)
        
        self.play(FadeOut(dot), FadeOut(esoph), FadeOut(stomach), FadeOut(intest))