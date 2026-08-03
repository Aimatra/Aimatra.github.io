"""
Animation Manim (style 3Blue1Brown) pour illustrer le principe de l'ACP :
on cherche l'axe qui MAXIMISE la variance (l'inertie) du nuage de points projeté.

Installation (une fois) :
    pip install manim
    # + FFmpeg installé sur la machine (obligatoire)
    # + une distribution LaTeX (facultatif, seulement si tu gardes MathTex)

Rendu de la vidéo :
    manim -pqh acp_projection.py ACPProjection
    # -p  : ouvre la vidéo une fois le rendu terminé
    # -qh : qualité "high" (1080p) ; utiliser -ql pour un rendu rapide en basse qualité

Le fichier vidéo est généré dans media/videos/acp_projection/1080p60/ACPProjection.mp4
"""

from manim import (
    Scene, Axes, Dot, Line, Rectangle, ValueTracker, VGroup, Text,
    always_redraw, Create, FadeIn, LaggedStartMap, Transform, Write, FadeOut,
    BLUE, YELLOW, GREEN, RED, WHITE, ORIGIN, RIGHT, LEFT, UP, DOWN, PI,
)
import numpy as np


class ACPProjection(Scene):
    def construct(self):
        # -------------------------------------------------------------
        # 1. Générer un nuage de points 2D corrélé (comme dans le cours)
        # -------------------------------------------------------------
        np.random.seed(42)
        n_points = 60
        covariance = [[3.0, 1.8], [1.8, 1.0]]
        donnees = np.random.multivariate_normal([0, 0], covariance, n_points)
        donnees = donnees - donnees.mean(axis=0)  # nuage centré, comme en ACP

        titre = Text("Analyse en Composantes Principales", font_size=32).to_edge(UP)
        self.play(Write(titre))

        axes = Axes(
            x_range=[-5, 5, 1], y_range=[-5, 5, 1],
            x_length=7, y_length=7,
        ).shift(LEFT * 1.5)

        points = VGroup(*[
            Dot(axes.c2p(x, y), radius=0.05, color=BLUE)
            for x, y in donnees
        ])

        self.play(Create(axes))
        self.play(LaggedStartMap(FadeIn, points, lag_ratio=0.02), run_time=2)
        self.wait(0.5)

        # -------------------------------------------------------------
        # 2. Faire tourner un axe candidat et mesurer la variance projetée
        # -------------------------------------------------------------
        angle = ValueTracker(0.0)

        def direction():
            a = angle.get_value()
            return np.array([np.cos(a), np.sin(a)])

        def ligne_axe():
            d = direction()
            return Line(
                axes.c2p(*(-4.5 * d)), axes.c2p(*(4.5 * d)), color=YELLOW
            )

        def variance_projetee():
            d = direction()
            projections = donnees @ d
            return float(np.var(projections))

        barre = always_redraw(
            lambda: Rectangle(
                height=max(variance_projetee(), 0.01),
                width=0.6,
                color=GREEN,
                fill_opacity=0.8,
            ).next_to(axes, RIGHT, buff=1).align_to(axes, DOWN)
        )
        label_barre = Text("Inertie expliquée", font_size=20).next_to(barre, DOWN)

        axe_candidat = always_redraw(ligne_axe)

        self.play(Create(axe_candidat), Create(barre), Write(label_barre))
        self.wait(0.3)

        # On balaye tous les angles de 0 à pi : la barre monte et redescend
        self.play(angle.animate.set_value(PI), run_time=6, rate_func=lambda t: t)
        self.wait(0.3)

        # -------------------------------------------------------------
        # 3. Se stabiliser sur le premier axe principal (variance max)
        # -------------------------------------------------------------
        matrice_cov = np.cov(donnees.T)
        valeurs_propres, vecteurs_propres = np.linalg.eigh(matrice_cov)
        ordre = np.argsort(valeurs_propres)[::-1]
        vecteurs_propres = vecteurs_propres[:, ordre]

        angle_pc1 = float(np.arctan2(vecteurs_propres[1, 0], vecteurs_propres[0, 0]))
        self.play(angle.animate.set_value(angle_pc1), run_time=2)

        label_pc1 = Text("Axe 1 (variance maximale)", font_size=22, color=YELLOW)
        label_pc1.next_to(axes, DOWN)
        self.play(Write(label_pc1))
        self.wait(1)

        # -------------------------------------------------------------
        # 4. Ajouter le second axe principal, orthogonal au premier
        # -------------------------------------------------------------
        angle_pc2 = angle_pc1 + PI / 2
        direction_pc2 = np.array([np.cos(angle_pc2), np.sin(angle_pc2)])
        axe2 = Line(
            axes.c2p(*(-4.5 * direction_pc2)), axes.c2p(*(4.5 * direction_pc2)),
            color=RED,
        )
        label_pc2 = Text("Axe 2 (orthogonal)", font_size=22, color=RED)
        label_pc2.next_to(label_pc1, DOWN)

        self.play(Create(axe2), Write(label_pc2))
        self.wait(1)

        # -------------------------------------------------------------
        # 5. Montrer la projection des points sur l'axe 1
        # -------------------------------------------------------------
        direction_pc1 = np.array([np.cos(angle_pc1), np.sin(angle_pc1)])
        projections_pc1 = donnees @ direction_pc1
        points_projetes = VGroup(*[
            Dot(axes.c2p(*(p * direction_pc1)), radius=0.05, color=YELLOW)
            for p in projections_pc1
        ])

        fleches_projection = VGroup(*[
            Line(pt.get_center(), pp.get_center(), color=WHITE, stroke_opacity=0.25)
            for pt, pp in zip(points, points_projetes)
        ])

        self.play(Create(fleches_projection), run_time=1.5)
        self.play(FadeIn(points_projetes))
        self.wait(2)

        self.play(
            FadeOut(fleches_projection), FadeOut(barre), FadeOut(label_barre),
            FadeOut(points_projetes),
        )
        self.wait(1)
