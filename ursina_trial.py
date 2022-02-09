from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from math import cos, sin, radians, tan

bullet_speed = 300 #m/s

app = Ursina()

floor_texture = load_texture('floor.png')
target_texture = load_texture('target.png')
sky_texture = load_texture('sky.jpg')

class target(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            scale_x=2,
            scale_y=2,
            scale_z=0.5,
            collider='box',
            color=color.white,
            position=(2, 3, 0),
            texture=target_texture
        )
    def update(self):
        origin = self.world_position
        hit_info = boxcast(origin, (0, 0, 1), ignore=(self,), distance=0, thickness=(3, 3, 3), debug=False)
        if hit_info.hit:
            destroy(self)

player = FirstPersonController()

Target = target()

gun_fire = Audio('gun_fire.mp3', loop=False, autoplay=False)

def distance(a, b):
    A = abs(a[0]-b[0])
    B = abs(a[1]-b[1])
    C = abs(a[2]-b[2])
    Distance = (A**2+B**2+C**2)**0.5
    return Distance

def gravity(x, theta, c):
    y = -(9.81/2)*(x/(bullet_speed*cos(radians(theta))))**2+tan(radians(theta))*x+c
    return y

def update():
    bullets = []
    if held_keys['left shift']:
        player.speed = 10
    else:
        player.speed = 5

    if held_keys['left mouse']:
        Bullet = bullet(position=Vec3(player.position.x, player.position.y+2, player.position.z), rotation=camera.world_rotation)
        bullets.append(Bullet)
        gun_fire.play()

    if held_keys['right mouse']:
        Target=target()

class bullet(Entity):
    def __init__(self, position, rotation):
        global theta3, c, bullet_count, theta_ro, direction
        super().__init__(
            model='cube',
            color=color.violet,
            position=Vec3(0, 0, 0),
            scale_x=0.2,
            scale_y=0.2,
            scale_z=0.5,
            collider='box',
            rotation=rotation
        )
        moving_x = 0
        moving_z = 0
        moving_y = 0
        theta = camera.world_rotation_y
        theta2 = camera.world_rotation_x

        if 0 <= theta <= 90:
            moving_x = 2 * cos(radians(90 - theta))
            moving_z = 2 * sin(radians(90 - theta))
        elif 90<theta<=180:
            moving_x = 2 * cos(radians(theta-90))
            moving_z = -2 * sin(radians(theta-90))
        elif -90<=theta<0:
            moving_x = -2* cos(radians(90+theta))
            moving_z = 2* sin(radians(90+theta))
        elif -180<=theta<-90:
            moving_x = -2*cos(radians(-theta-90))
            moving_z = -2*sin(radians(-theta-90))

        if 0<=theta2<=90:
            moving_y = -2*sin(radians(theta2))
        elif -90<=theta2<0:
            moving_y = 2*sin(radians(-theta2))

        new_position = position+Vec3(moving_x, moving_y, moving_z).normalized()
        self.position = new_position
        direction = Vec3(moving_x, moving_y, moving_z).normalized()
        theta3 = -camera.world_rotation_x
        theta_ro = camera.world_rotation_y
        c = camera.world_position.y
        bullet_count = 0

    def update(self):
        global theta3, c, bullet_count, theta_ro, direction
        y = gravity(bullet_count * 0.5, theta3, c)
        if theta3>=0:
            if bullet_count < 10000:
                if y>0:
                    if 0<=theta_ro<=90:
                        self.position = Vec3(self.position.x + (bullet_count * 0.5)*cos(radians(90-theta_ro)), y, self.position.z + (bullet_count*0.5)*sin(radians(90-theta_ro)))
                    elif 90<theta_ro<=180:
                        self.position = Vec3(self.position.x + (bullet_count * 0.5)*cos(radians(theta_ro-90)), y, self.position.z - (bullet_count*0.5)*sin(radians(theta_ro-90)))
                    elif -90<=theta_ro<0:
                        self.position = Vec3(self.position.x - (bullet_count * 0.5)*cos(radians(90+theta_ro)), y, self.position.z + (bullet_count*0.5)*sin(radians(theta_ro+90)))
                    elif -180<=theta_ro<-90:
                        self.position = Vec3(self.position.x - (bullet_count * 0.5)*cos(radians(-theta_ro-90)), y, self.position.z - (bullet_count*0.5)*sin(radians(-theta_ro-90)))

                    bullet_count += 1
                else:
                    destroy(self)
            else:
                destroy(self)
        else:
            if self.position.y>0:
                move_y = -sin(radians(-theta3))
                if 0 <= theta_ro <= 90:
                    move_x = cos(radians(90-theta_ro))
                    move_z = sin(radians(90-theta_ro))
                elif 90<theta_ro<=180:
                    move_x = cos(radians(theta_ro-90))
                    move_z = -sin(radians(theta_ro-90))
                elif -90<=theta_ro<0:
                    move_x = -cos(radians(90+theta_ro))
                    move_z = sin(radians(theta_ro+90))
                elif -180<=theta_ro<-90:
                    move_x = -cos(radians(-theta_ro-90))
                    move_z = -sin(radians(-theta_ro-90))

                self.position = Vec3(self.position.x+move_x*bullet_count*0.5, self.position.y+move_y*bullet_count*0.5, self.position.z+move_z*bullet_count*0.5)
                bullet_count += 1
            else:
                destroy(self)

        try:
            origin = self.world_position + (self.up*.5)
            hit_info = boxcast(origin, direction, ignore=(self, player,), thickness=(0.2, 0.2), distance=0, debug=False)
            if hit_info.hit:
                destroy(self)
        except:
            destroy(self)

floor = Entity(model='cube', scale_x=100, scale_z=100, collider='box', color=color.brown, texture=floor_texture)
wall1 = Entity(model='cube', scale_x=100, scale_y=100, collider='box', color=color.green, position=(0, 0, 50))
wall2 = Entity(model='cube', scale_x=100, scale_y=100, collider='box', color=color.blue, position=(0, 0, -50))
wall3 = Entity(model='cube', scale_z=100, scale_y=100, collider='box', color=color.red, position=(50, 0, 0))
wall4 = Entity(model='cube', scale_z=100, scale_y=100, collider='box', color=color.yellow, position=(-50, 0, 0))

sky = Entity(model='sphere', scale=200, double_sided=True, texture=sky_texture)

app.run()