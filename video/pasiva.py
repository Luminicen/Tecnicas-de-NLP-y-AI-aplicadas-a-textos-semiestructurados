from manim import *

class ConversorPasivaActiva(Scene):
    def construct(self):
        # 1. Título
        titulo = Text("Conversor de Voz Pasiva a Activa", font_size=48, gradient=(BLUE, GREEN))
        self.play(Write(titulo))
        self.wait(2)
        self.play(FadeOut(titulo))

        # 2. Frase en pasiva
        frase_pasiva = Text("El libro fue escrito por Gabriel García Márquez", font_size=36)
        self.play(Write(frase_pasiva))
        self.wait(1)

        # Sujeto paciente
        sujeto = SurroundingRectangle(frase_pasiva[0:6], color=YELLOW, buff=0.3)
        brace_sujeto = Brace(sujeto, direction=DOWN, buff=0.1)
        label_sujeto = Text("Sujeto", font_size=24)
        label_sujeto.next_to(brace_sujeto, DOWN, buff=0.05)
        self.play(Create(sujeto), GrowFromCenter(brace_sujeto), Write(label_sujeto))
        self.wait(1)

        # Verbo en participio + auxiliar
        verbo = SurroundingRectangle(frase_pasiva[8:19], color=RED, buff=0.2)
        brace_verbo = Brace(verbo, direction=DOWN, buff=0.1)
        label_verbo = Text("Verbo en participio + auxiliar", font_size=24)
        label_verbo.next_to(brace_verbo, DOWN, buff=0.05)
        # Desaparece el anterior texto y rectángulo
        self.play(FadeOut(sujeto), FadeOut(label_sujeto),FadeOut(brace_sujeto), Create(verbo), GrowFromCenter(brace_verbo), Write(label_verbo))
        self.wait(1)

        # Complemento agente
        agente = SurroundingRectangle(frase_pasiva[21:], color=GREEN, buff=0.4)
        brace_agente = Brace(agente, direction=DOWN, buff=0.1)
        label_agente = Text("Agente", font_size=24)
        label_agente.next_to(brace_agente, DOWN, buff=0.05)
        self.play(FadeOut(verbo), FadeOut(label_verbo),FadeOut(brace_verbo), Create(agente), GrowFromCenter(brace_agente), Write(label_agente))
        self.wait(2)
        self.play(FadeOut(agente), FadeOut(label_agente), FadeOut(brace_agente))



        # 4. Transformación a activa
        frase_activa = Text("Gabriel García Márquez escribió el libro", font_size=36, color=GREEN)
        self.play(Transform(frase_pasiva, frase_activa))
        self.wait(2)

        # 5. Resultado final vistoso
        resultado = Text("¡Conversión completada!", font_size=40, gradient=(BLUE, PINK))
        resultado.next_to(frase_activa, DOWN, buff=1)
        self.play(Write(resultado))
        self.wait(3)
