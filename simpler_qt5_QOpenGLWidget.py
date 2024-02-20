import sys, signal
import numpy as np
import moderngl

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QSurfaceFormat

def make_qt_format():
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    return fmt

class StimDisplay(QOpenGLWidget):
    def __init__(self, app):
        super().__init__()
        self.setFormat(make_qt_format())

        self.app = app

        self.ctx = None
        self.vao = None

        self.subscreen_viewports = [(0, 0, 100, 100),
                                    (101, 0, 100, 100)]

        self.frame_cnt = 0

    def initializeGL(self):
        # Create ModernGL context
        self.ctx = moderngl.create_context()

        # Triangle vertices (x, y)
        vertices = np.array([
            -0.6, -0.6,
             0.6, -0.6,
             0.0,  0.6
        ], dtype='f4')

        # Vertex Buffer Object
        vbo = self.ctx.buffer(vertices)

        # Vertex Array Object
        self.vao = self.ctx.simple_vertex_array(
            self.ctx.program(
                vertex_shader="""
                #version 330
                in vec2 in_vert;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
                """,
                fragment_shader="""
                #version 330
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red color
                }
                """,
            ),
            vbo,
            'in_vert'
        )

        # Clear the buffer
        # self.ctx.fbo.clear(0, 0, 0, 1)
        print('Initial clearing to 0.')

    def paintGL(self):
        print(f"Frame # {self.frame_cnt}")

        fbo = self.ctx.detect_framebuffer()
        fbo.use()

        # Clear subscreen 1
        self.ctx.fbo.clear(0.5, 0.5, 0.5, 1.0, viewport=self.subscreen_viewports[1])

        # Render the triangle in subscreen 0
        self.ctx.viewport = self.subscreen_viewports[0]
        self.vao.render(moderngl.TRIANGLES)
        self.ctx.fbo.release()

        self.frame_cnt += 1

def main():

    # set default format with OpenGL context
    QSurfaceFormat.setDefaultFormat(make_qt_format())

    # launch application
    app = QtWidgets.QApplication([])

    # create the StimDisplay object
    stim_display = StimDisplay(app=app)
    stim_display.setGeometry(100, 100, 200, 200)
    stim_display.show()

    ####################################
    # Run QApplication
    ####################################

    # Use Ctrl+C to exit.
    # ref: https://stackoverflow.com/questions/2300401/qapplication-how-to-shutdown-gracefully-on-ctrl-c
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
