"""
Rose 3D (surface de Paul Nylander) — Manim
============================================

LA FORMULE COMPLÈTE (la capture d'écran n'en montrait que 3 lignes sur 5 !)

Deux paramètres indépendants :
    u     ∈ [0, 1]        -> "le long du pétale", du coeur vers le bord
    theta ∈ [-2π, 15π]    -> l'angle, ~8 tours : c'est ce qui empile les pétales

    phi(theta) = (π/2)·exp(-theta/(8π))                    torsion, décroît vers 0
    X(theta)   = 1 - ½·( (5/4)·(1 - (3.6·theta mod 2π)/π)² - ¼ )²   profil de pétale
    y(u)       = 1.95653·u²·(1.27689·u - 1)²·sin(phi)      courbure du pétale
    r          = X·( u·sin(phi) + y·cos(phi) )             rayon (PAS r = theta !)

    (x, y, z)  = ( r·sin(theta), r·cos(theta), X·(u·cos(phi) - y·sin(phi)) )

⚠️ Les deux pièges :
  1. Le "x" dans l'équation du z n'est PAS la coordonnée x, c'est le paramètre u.
  2. Le "X(...)" du z est une MULTIPLICATION par X, pas X composée avec (...).
  Et r n'est pas libre : il se calcule à partir de X, u, y et phi.

Le 3.6 dans X contrôle le nombre de pétales par tour. phi qui décroît fait que
les pétales du coeur sont très enroulés et ceux du bord s'ouvrent à plat.

Source de la formule : https://pgfplots.net/rose/  (d'après Paul Nylander)

---------------------------------------------------------------------------
RENDU — le point important pour la fluidité
---------------------------------------------------------------------------
Le mode -ql rend en 15 images/seconde : c'est ÇA qui rend l'animation
saccadée, pas le script. Pour une animation fluide, force 30 fps :

    manim -ql --fps 30 rose_3d.py Rose3D      # brouillon fluide (480p, 30fps)
    manim -qh rose_3d.py Rose3D               # final (1080p, 60fps, TRÈS long)

Astuce : garde resolution=(20, 220) tant que tu bricoles, et ne monte à
(30, 400) que pour le rendu final.
"""

import numpy as np
from manim import *

# Dégradé : couleur du coeur (haut) -> couleur des pétales extérieurs (bas)
COEUR = "#7B1030"   # bordeaux profond
BORD = "#FF8FB1"    # rose clair


class Rose3D(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-70 * DEGREES, zoom=1.35)
        self.begin_ambient_camera_rotation(rate=0.12)

        # --- Axes (calés sur la taille réelle de la rose : x,y ∈ [-2.2, 2.2],
        #     z ∈ [-1.2, 2.1]). x_length = amplitude du range -> échelle 1:1.
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[-1.5, 2.5, 1],
            x_length=5,
            y_length=5,
            z_length=4,
            axis_config={"stroke_width": 2, "stroke_opacity": 0.5},
        )
        self.add(axes)

        # --- La surface ---
        def rose_point(u, theta):
            phi = (PI / 2) * np.exp(-theta / (8 * PI))
            X = 1 - 0.5 * ((5 / 4) * (1 - np.mod(3.6 * theta, 2 * PI) / PI) ** 2 - 1 / 4) ** 2
            y = 1.95653 * u**2 * (1.27689 * u - 1) ** 2 * np.sin(phi)
            r = X * (u * np.sin(phi) + y * np.cos(phi))
            return np.array([
                r * np.sin(theta),
                r * np.cos(theta),
                X * (u * np.cos(phi) - y * np.sin(phi)),
            ])

        surface = Surface(
            lambda u, v: rose_point(u, v),
            u_range=[0, 1],                 # u : le long du pétale
            v_range=[-2 * PI, 15 * PI],     # theta : ~8 tours -> couches de pétales
            # (résolution en u, en theta) : monte à (30, 400) pour le rendu final
            resolution=(30, 400),
            fill_opacity=1,
        )
        surface.scale(2.2)

        # --- Dégradé : chaque facette est colorée selon sa hauteur z.
        #     Le coeur de la rose est la partie haute -> bordeaux profond,
        #     les pétales extérieurs retombent -> rose clair.
        zs = np.array([face.get_center()[2] for face in surface])
        z_min, z_max = zs.min(), zs.max()
        for face, z in zip(surface, zs):
            alpha = (z - z_min) / (z_max - z_min)  # 0 en bas, 1 en haut
            face.set_fill(interpolate_color(ManimColor(BORD), ManimColor(COEUR), alpha),
                          opacity=1)

        surface.set_stroke(width=0.4, color="#FFD3E0", opacity=0.35)

        # --- Animation progressive ---
        self.play(Create(surface), run_time=6, rate_func=linear)
        self.wait(1.5)
