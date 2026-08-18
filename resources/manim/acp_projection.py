"""
Animation Manim pour l'introduction du cours d'ACP.

Trois scènes, à assembler/rendre séparément puis à concaténer (ou à jouer à la
suite dans une seule vidéo finale) :

  1. TableauVersNuage   : un tableau de données ; chaque ligne se colore, et
                          un point de la même couleur apparaît sur le nuage de
                          points à droite. Fait pour 3 lignes, puis on ajoute
                          le reste du nuage d'un coup.

  2. PonderationTransform : on introduit 3 matrices de poids D différentes et
                          on montre comment elles "tordent" visuellement le
                          nuage (ici représenté par la taille des points, qui
                          grossissent avec leur poids p_i).

  3. MetriqueFleche     : on introduit la métrique M, avec une flèche reliant
                          deux points du nuage pour expliquer visuellement
                          d_M^2(x_i, x_j).

Pour générer une scène en particulier :
    manim -pqh acp_intro.py TableauVersNuage
    manim -pqh acp_intro.py PonderationTransform
    manim -pqh acp_intro.py MetriqueFleche
"""

from manim import *

# ---------------------------------------------------------------------------
# Données d'exemple (reprises du cours : PIB / Chômage, à l'échelle réduite
# pour que ça rentre proprement dans le cadre)
# ---------------------------------------------------------------------------

DONNEES = [
    ("France",      3.0, 2.0, 1.5),
    ("Allemagne",   4.2, 1.4, 1.9),
    ("États-Unis",  5.5, 0.8, 2.9),
    ("Japon",       1.8, 0.4, 2.5),
    ("Brésil",     -0.5, 1.9, 4.5),
    ("Norvège",     5.9, 0.7, 3.0),
    ("Suède",       3.4, 1.1, 2.0),
    ("Italie",      1.2, 2.4, 1.8),
    ("Espagne",     0.6, 2.0, 2.2),
    ("Portugal",   -0.3, 1.6, 1.7),
]

COULEURS = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, TEAL, PINK, MAROON, GOLD]


# ---------------------------------------------------------------------------
# Scène 1 : du tableau au nuage de points
# ---------------------------------------------------------------------------

class TableauVersNuage(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, distance=8)

        titre = Text("1. Les concepts importants", font_size=28)
        titre.to_corner(UL)
        self.add_fixed_in_frame_mobjects(titre)
        self.play(Write(titre))

        # --- Le tableau (reste plat, affiché à l'écran) --------------------
        table_data = [["Pays", "PIB", "Chômage", "Inflation"]] + [
            [nom, f"{pib:.1f}", f"{chom:.1f}", f"{inf:.1f}"]
            for nom, pib, chom, inf in DONNEES[:6]
        ]
        table = Table(table_data, include_outer_lines=True).scale(0.35)
        table.to_corner(UL)
        self.add_fixed_in_frame_mobjects(table)
        self.play(Create(table))
        self.wait(0.5)

        # --- Les axes 3D -----------------------------------------------
        axes = ThreeDAxes(
            x_range=[-2, 7, 1],
            y_range=[-1, 3, 1],
            z_range=[0, 5, 1],
            x_length=5.5,
            y_length=4,
            z_length=4,
        )
        self.play(Create(axes))

        x_label = Text("PIB", font_size=22).next_to(axes.x_axis.get_end(), RIGHT)
        y_label = Text("Chômage", font_size=22).next_to(axes.y_axis.get_end(), UP)
        z_label = Text("Inflation", font_size=22).next_to(axes.z_axis.get_end(), OUT)
        for label in (x_label, y_label, z_label):
            self.add_fixed_orientation_mobjects(label)
        self.play(Write(x_label), Write(y_label), Write(z_label))
        self.wait(0.3)

        # --- Les 3 premières lignes, une par une ---------------------------
        points_deja_places = []

        for i in range(3):
            nom, pib, chom, inf = DONNEES[i]
            couleur = COULEURS[i]

            ligne_cells = table.get_rows()[i + 1]
            self.play(
                *[cell.animate.set_color(couleur) for cell in ligne_cells],
                run_time=0.6,
            )

            point = Sphere(radius=0.08, color=couleur)
            point.move_to(axes.coords_to_point(pib, chom, inf))
            self.play(FadeIn(point, scale=0.5), run_time=0.6)
            points_deja_places.append(point)
            self.wait(0.3)

        self.wait(0.5)

        # --- Le reste du nuage, ajouté d'un coup ---------------------------
        reste = VGroup()
        for nom, pib, chom, inf in DONNEES[3:]:
            s = Sphere(radius=0.06, color=GREY_B)
            s.move_to(axes.coords_to_point(pib, chom, inf))
            reste.add(s)

        self.play(
            LaggedStartMap(FadeIn, reste, scale=0.5, lag_ratio=0.1),
            run_time=1.5,
        )
        self.wait(0.5)

        # --- Petite rotation de caméra pour bien montrer la 3D -------------
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(4)
        self.stop_ambient_camera_rotation()

        conclusion = Text(
            "Chaque ligne du tableau devient un point du nuage",
            font_size=22,
        ).to_corner(DR)
        self.add_fixed_in_frame_mobjects(conclusion)
        self.play(Write(conclusion))
        self.wait(2)

# ---------------------------------------------------------------------------
# Scène 2 : trois matrices de poids, et la déformation visuelle du nuage
# ---------------------------------------------------------------------------

class PonderationTransform(Scene):
    def construct(self):
        titre = Text("La matrice de poids D", font_size=32).to_edge(UP)
        self.play(Write(titre))

        axes = Axes(
            x_range=[-2, 7, 1],
            y_range=[-1, 3, 1],
            x_length=6,
            y_length=4.2,
        )
        axes.move_to(ORIGIN).shift(0.3 * DOWN)

        self.play(Create(axes))

        # Nuage de points de départ (poids égaux)
        n = len(DONNEES)
        poids_egaux = [1 / n] * n

        dots = VGroup(
            *[
                Dot(axes.coords_to_point(pib, chom), color=BLUE, radius=0.08)
                for _, pib, chom in DONNEES
            ]
        )
        self.play(LaggedStartMap(FadeIn, dots, lag_ratio=0.05))
        self.wait(0.5)

        formule_D = MathTex(
            r"D = \mathrm{diag}(p_1, \dots, p_n)"
        ).to_edge(DOWN)
        self.play(Write(formule_D))
        self.wait(1)

        # --- Trois jeux de poids différents, appliqués un par un -----------
        # Poids égaux (référence), puis deux pondérations différentes.
        poids_uniforme = [1 / n] * n
        poids_pib = _normaliser([max(pib, 0.1) for _, pib, chom in DONNEES])
        poids_inverse_pib = _normaliser(
            [1 / max(pib, 0.1) if pib > 0 else 3 for _, pib, chom in DONNEES]
        )

        jeux_de_poids = [
            (r"D_1 : \text{poids égaux}", poids_uniforme),
            (r"D_2 : \text{poids} \propto \text{PIB}", poids_pib),
            (r"D_3 : \text{poids} \propto 1/\text{PIB}", poids_inverse_pib),
        ]

        label_actuel = None

        for tex, poids in jeux_de_poids:
            nouveau_label = MathTex(tex, font_size=32).next_to(formule_D, UP)

            if label_actuel is None:
                self.play(Write(nouveau_label))
            else:
                self.play(Transform(label_actuel, nouveau_label))

            if label_actuel is None:
                label_actuel = nouveau_label

            # La taille de chaque point reflète son poids p_i : plus le poids
            # est grand, plus le point "pèse" visuellement dans le nuage.
            anims = []
            for dot, p in zip(dots, poids):
                rayon_cible = 0.05 + 0.35 * (p * n)  # normalisé autour de 0.08
                anims.append(dot.animate.scale_to_fit_width(2 * rayon_cible))
            self.play(*anims, run_time=1.2)
            self.wait(1)

        conclusion = Text(
            "Changer D change l'importance relative de chaque observation",
            font_size=24,
        )
        conclusion.next_to(axes, DOWN, buff=1.2)
        self.play(FadeOut(formule_D), FadeOut(label_actuel), Write(conclusion))
        self.wait(2)


def _normaliser(poids_bruts):
    total = sum(poids_bruts)
    return [p / total for p in poids_bruts]


# ---------------------------------------------------------------------------
# Scène 3 : la métrique M et la distance entre deux points
# ---------------------------------------------------------------------------

class MetriqueFleche(Scene):
    def construct(self):
        titre = Text("La métrique M et la distance entre observations", font_size=30)
        titre.to_edge(UP)
        self.play(Write(titre))

        axes = Axes(
            x_range=[-2, 7, 1],
            y_range=[-1, 3, 1],
            x_length=6,
            y_length=4.2,
        )
        axes.move_to(ORIGIN).shift(0.2 * DOWN)
        self.play(Create(axes))

        dots = VGroup(
            *[
                Dot(axes.coords_to_point(pib, chom), color=BLUE_D, radius=0.07)
                for _, pib, chom in DONNEES
            ]
        )
        self.play(FadeIn(dots))
        self.wait(0.5)

        # On choisit deux points précis à relier (x_i et x_j)
        i, j = 0, 4  # France et Brésil, par exemple
        nom_i, pib_i, chom_i = DONNEES[i]
        nom_j, pib_j, chom_j = DONNEES[j]

        point_i = dots[i]
        point_j = dots[j]

        self.play(
            point_i.animate.set_color(RED).scale(1.4),
            point_j.animate.set_color(ORANGE).scale(1.4),
        )

        label_i = Text(nom_i, font_size=20, color=RED).next_to(point_i, UP, buff=0.15)
        label_j = Text(nom_j, font_size=20, color=ORANGE).next_to(point_j, DOWN, buff=0.15)
        self.play(Write(label_i), Write(label_j))
        self.wait(0.5)

        fleche = Arrow(
            point_i.get_center(), point_j.get_center(),
            buff=0.1, color=WHITE, stroke_width=3,
        )
        self.play(GrowArrow(fleche))
        self.wait(0.5)

        formule = MathTex(
            r"d_M^2(x_i, x_j) = (x_i - x_j)^\top M (x_i - x_j)",
            font_size=34,
        ).to_edge(DOWN)
        self.play(Write(formule))
        self.wait(1)

        # On fait ensuite apparaître deux choix de M, pour montrer que la
        # distance mesurée par la flèche change selon la métrique choisie.
        m_euclid = MathTex(r"M = I_p \quad \text{(distance brute)}", font_size=28)
        m_euclid.next_to(formule, UP)
        self.play(Write(m_euclid))
        self.wait(1.5)

        m_norm = MathTex(
            r"M = \mathrm{diag}(1/s_1^2, \dots, 1/s_p^2) \quad \text{(distance normalisée)}",
            font_size=28,
        ).next_to(formule, UP)
        self.play(Transform(m_euclid, m_norm))

        # La flèche "se déforme" pour suggérer que la distance perçue change
        # selon la métrique (ici on joue simplement sur son épaisseur/couleur
        # pour représenter symboliquement le changement d'échelle).
        fleche_deformee = Arrow(
            point_i.get_center(), point_j.get_center(),
            buff=0.1, color=YELLOW, stroke_width=7,
        )
        self.play(Transform(fleche, fleche_deformee))
        self.wait(2)

        conclusion = Text(
            "Le choix de M change la notion même de distance",
            font_size=24,
        )
        conclusion.next_to(axes, DOWN, buff=1.4)
        self.play(FadeOut(m_euclid), Write(conclusion))
        self.wait(2)
