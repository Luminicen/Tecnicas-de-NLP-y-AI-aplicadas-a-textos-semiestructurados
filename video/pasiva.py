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

        frase_lema = Text("El libro escribir por Gabriel García Márquez", font_size=36, color=ORANGE)
        frase_lema.next_to(frase_pasiva, DOWN, buff=0.5)
        etiqueta = Text("Lematización", font_size=24, color=BLUE).next_to(frase_lema, DOWN, buff=0.2)

        self.play(Write(frase_lema), Write(etiqueta))
        self.wait(2)

        # Animación de transformación desde el original a la forma lematizada
        self.play(Transform(frase_pasiva, frase_lema))
        self.wait(2)
        self.play(FadeOut(etiqueta))
        
        
        # --- Desaparece la frase pasiva completa ---
        self.play(FadeOut(frase_pasiva))
        self.wait(1)

        # --- Dividir en bloques para mostrar correspondencia ---
        palabras_pasiva = ["fue escrito"]
        palabras_lema = ["escribir"]

        txt_pasiva = [Text(w, font_size=28).to_edge(UP, buff=1.5) for w in palabras_pasiva]
        txt_lema = [Text(w, font_size=28).next_to(txt_pasiva[i], DOWN*4) for i, w in enumerate(palabras_lema)]

        # Mostrar los textos originales (arriba) y lematizados (abajo)
        for up, down in zip(txt_pasiva, txt_lema):
            self.play(Write(up), Write(down))

        self.wait(1)

        # --- Flechas que muestran la correspondencia ---
        flechas = []
        for up, down in zip(txt_pasiva, txt_lema):
            flecha = Arrow(start=up.get_bottom(), end=down.get_top(), buff=0.1, color=YELLOW)
            flechas.append(flecha)
            self.play(Create(flecha))

        self.wait(2)

        # --- Limpiar para seguir con el paso de conversión activa ---
        self.play(*[FadeOut(m) for m in txt_pasiva + txt_lema + flechas + [etiqueta]])
        self.wait(1)
        
        # --- Separar palabras de la frase lematizada ---
        palabras = ["El libro", "escribir", "por", "Gabriel García Márquez"]
        mobjects = [Text(w, font_size=32, color=WHITE) for w in palabras]

        # Colocar cada palabra alineada en fila (para manipularlas individualmente)
        for i, mob in enumerate(mobjects):
            mob.move_to(np.array([-6 + i*2.5, 0, 0]))  # posiciones en fila
            self.play(Write(mob))
        self.wait(1)

        # --- Definir posiciones finales (voz activa) ---
        finales = ["Gabriel García Márquez", "escribir", "el libro"]
        targets = [Text(w, font_size=32, color=GREEN) for w in finales]

        for i, t in enumerate(targets):
            t.move_to(np.array([-4 + i*4, -2, -1]))
            t.shift(DOWN * (t.get_center()[1] - 2))  # posiciones en la parte de abajo
        # Desaparecer "por" porque ya no se usa
        self.play(FadeOut(mobjects[2]))
        # --- Asignar targets de movimiento ---
        # mover "Gabriel García Márquez"
        mobjects[3].generate_target()
        mobjects[3].target.move_to(targets[0].get_center())

        # mover "escribir"
        mobjects[1].generate_target()
        mobjects[1].target.move_to(targets[1].get_center())

        # mover "El libro" (pasa a "el libro" → cambio de color también)
        mobjects[0].generate_target()
        mobjects[0].target.move_to(targets[2].get_center()).set_color(GREEN)

        
        self.play(FadeOut(frase_lema))

        # --- Animar el reordenamiento ---
        self.play(
            MoveToTarget(mobjects[3]),
            MoveToTarget(mobjects[1]),
            MoveToTarget(mobjects[0]),
            run_time=2
        )
        self.wait(2)
        
        # --- Mostrar frase activa final ---
        self.play(FadeOut(mobjects[1],mobjects[3],mobjects[0]))
        frase_activa = Text("Gabriel García Márquez escribir el libro", font_size=36, color=GREEN)
        
        self.play(Write(frase_activa))
        self.wait(2)
        

        # 5. Resultado final vistoso
        resultado = Text("¡Conversión completada!", font_size=40, gradient=(BLUE, PINK))
        resultado.next_to(frase_activa, DOWN, buff=1)
        self.play(Write(resultado))
        self.wait(3)
