"""
Rose 3D animée progressivement — Manim
========================================

Ta formule (celle du reel Instagram) :

    r = theta                                  (spirale : le rayon grandit avec theta)

    phi(theta) = (pi/2) * exp(-theta / (8*pi))  (angle de torsion, décroît vers 0)

    X(theta) = 1 - 1/2 * ( 5/4 * (1 - (theta mod 2*pi)/pi)^2 - 1/4 )^2
                                                 (profil d'un pétale, période 2*pi)

    (x, y, z) = ( r*sin(theta),
                  r*cos(theta),
                  X( x*cos(phi) - y*sin(phi) ) )   <- attention : ce x,y sont
                                                        ceux qu'on vient de calculer,
                                                        pas theta directement.

Pour l'effet "se dessine petit à petit", Manim a un outil dédié :
la classe ParametricFunction + l'animation Create(), qui trace la
courbe progressivement du premier au dernier point tout seul.

Installation (une seule fois, sur ta machine) :
    pip install manim
    (+ ffmpeg et les libs pango/cairo si besoin, selon ton OS)

Pour lancer le rendu (qualité basse, rapide, pour itérer) :
    manim -pql rose_3d.py Rose3D

Pour la qualité finale (plus lent, meilleure résolution) :
    manim -pqh rose_3d.py Rose3D
"""

import numpy as np
from manim import *


class Rose3D(ThreeDScene):
    def construct(self):
        # --- 1. Réglage de la caméra 3D ---
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.15)  # légère rotation auto

        axes = ThreeDAxes(
            x_range=[-30, 30, 10],
            y_range=[-30, 30, 10],
            z_range=[-2, 2, 1],
        )
        self.add(axes)

        # --- 2. Ta fonction ---
        def phi(theta):
            return (PI / 2) * np.exp(-theta / (8 * PI))

        def X(t):
            # t ici est déjà l'argument "tourné" (x*cos(phi) - y*sin(phi)),
            # PAS theta directement -> on le fait quand même passer "mod 2*pi"
            # pour rester dans une période valide de la fonction profil.
            u = np.mod(t, 2 * PI)
            return 1 - 0.5 * ((5 / 4) * (1 - u / PI) ** 2 - 1 / 4) ** 2

        def rose_point(theta):
            r = theta  # ta spirale : r = theta
            p = phi(theta)
            x = r * np.sin(theta)
            y = r * np.cos(theta)
            z = X(x * np.cos(p) - y * np.sin(p))
            return np.array([x, y, z])

        # --- 3. Construction de la courbe paramétrique ---
        # theta va de 0 à plusieurs tours (2*pi par tour). Ajuste le nombre
        # de tours pour avoir plus ou moins de "couches" de pétales.
        n_tours = 10
        curve = ParametricFunction(
            rose_point,
            t_range=[0.01, n_tours * 2 * PI, 0.02],
            color=BLUE,
        ).scale(0.15)  # r=theta grandit vite -> on réduit l'échelle pour que ça tienne à l'écran

        # --- 4. Animation progressive : Create() dessine la courbe
        #         point par point, du début à la fin ---
        self.play(Create(curve), run_time=10, rate_func=linear)
        self.wait(2)
