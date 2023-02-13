class Vector3D:
    def __init__(self, *args):
        match len(args):
            case 2:
                #headingxy
                self.mX = 1
                self.mY = 1
                self.mZ = 0
            case 3:
                self.mX = float(args[0])
                self.mY = float(args[1])
                self.mZ = float(args[2])
            case _:
                self.mX = 0.0
                self.mY = 0.0
                self.mZ = 0.0


m1 = Vector3D(1,2,3)
print(m1.mX, m1.mY, m1.mZ)

