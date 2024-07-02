# ZenGL Test

Just a testing repository for zengl and learning to use it on the web.

## NOTES

Running this on zengl 2.4.0 or 2.5.0 with python <3.12 will eventually result in dealloc crash due to zengl, a temp fix was made but if you encounter an `Fatal Python error: none_dealloc` issue when using zengl, just switch to 3.12 or downgrade your version. More information can be found on the moderngl server(zengl is made by the same guy who has made moderngl)

## Pygbag(run on the web)

install pygbag: `pip install pygbag`
and then do: `pygbag --template noctx.tmpl .`

## Credits

Big thanks to `@dom0196` and `Szabolcs Dombi` from moderngl server for the help and examples they gave. Most of the shader pipeline code is from `@dom0196`'s [pygame spring jam game](https://github.com/d-orm/pgce_2024_spring_jam/tree/main). You can go and take a look at his game here: [Atomic Convection on Itch.io](https://djorm.itch.io/atomic-convection)

## Where did I get the shaders

https://github.com/opatut/Shaders/blob/master/data/underwater.glsl -> underwater shader

https://deep-fold.itch.io/pixel-planet-generator --> planet2 frag

planet.frag --> combination of functions from `planet2.frag`, [@HmarDev](https://github.com/HmarVR)'s code and some of my custom code

https://www.shadertoy.com/view/XtjcRd
https://www.shadertoy.com/view/XttyRX
https://www.shadertoy.com/view/MsKXzD
