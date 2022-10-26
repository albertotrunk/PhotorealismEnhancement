'''
Created on 18.09.2020

@author: rizka
'''
# !/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import glob
import os
import sys
import time
from subprocess import call
import subprocess
import shutil
import random
import string

try:
    sys.path.append(glob.glob('/opt/carla-simulator/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:

    print("NOOOOOOOOOOOOOOO")
    pass

import carla

from carla import VehicleLightState as vls

import argparse
import logging
from numpy import random


IM_width = 960
IM_Hight = 540
fov = 105

def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []

def main(index = 0):


    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=100,
        type=int,
        help='Number of vehicles (default: 30)')
    argparser.add_argument(
        '-w', '--number-of-walkers',
        metavar='W',
        default=50,
        type=int,
        help='Number of walkers (default: 10)')
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='Avoid spawning vehicles prone to accidents')
    argparser.add_argument(
        '--filterv',
        metavar='PATTERN',
        default='vehicle.*',
        help='Filter vehicle model (default: "vehicle.*")')
    argparser.add_argument(
        '--generationv',
        metavar='G',
        default='All',
        help='restrict to certain vehicle generation (values: "1","2","All" - default: "All")')
    argparser.add_argument(
        '--filterw',
        metavar='PATTERN',
        default='walker.pedestrian.*',
        help='Filter pedestrian type (default: "walker.pedestrian.*")')
    argparser.add_argument(
        '--generationw',
        metavar='G',
        default='2',
        help='restrict to certain pedestrian generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--tm-port',
        metavar='P',
        default=8000,
        type=int,
        help='Port to communicate with TM (default: 8000)')
    argparser.add_argument(
        '--asynch',
        action='store_true',
        help='Activate asynchronous mode execution')
    argparser.add_argument(
        '--hybrid',
        action='store_true',
        help='Activate hybrid mode for Traffic Manager')
    argparser.add_argument(
        '-s', '--seed',
        metavar='S',
        type=int,
        help='Set random device seed and deterministic mode for Traffic Manager')
    argparser.add_argument(
        '--seedw',
        metavar='S',
        default=0,
        type=int,
        help='Set the seed for pedestrians module')
    argparser.add_argument(
        '--car-lights-on',
        action='store_true',
        default=False,
        help='Enable automatic car light management')
    argparser.add_argument(
        '--hero',
        action='store_true',
        default=False,
        help='Set one of the vehicles as hero')
    argparser.add_argument(
        '--respawn',
        action='store_true',
        default=False,
        help='Automatically respawn dormant vehicles (only in large maps)')
    argparser.add_argument(
        '--no-rendering',
        action='store_true',
        default=False,
        help='Activate no rendering mode')

    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)



    #os.system("/opt/carla-simulator/CarlaUE4.sh -RenderOffScreen")
    #call(["/opt/carla-simulator/CarlaUE4.sh", ""])#-RenderOffScreen
    subprocess.Popen(["/opt/carla-simulator/CarlaUE4.sh", "-RenderOffScreen" ] )

    time.sleep(30)

    print("done")
    actor_list = []
    vehicles_list = []
    walkers_list = []
    all_id = []
    client = carla.Client(args.host, args.port)
    client.set_timeout(1.0)
    synchronous_master = False
    random.seed(args.seed if args.seed is not None else int(time.time()))

    try:
        print("ok")
        #world = client.get_world()
        Town = random.choice(["Town01" ,"Town02" ,"Town03" ,"Town04" ,"Town05" ,"Town06" ,"Town07" ,"Town08" ,"Town09" ,"Town10"  ])
        world = client.load_world(Town)
        blueprint_library = world.get_blueprint_library()

        vehicle_bp = blueprint_library.filter('audi')[0]
        point0 = random.choice(world.get_map().get_spawn_points())

        vehicle = world.spawn_actor(vehicle_bp, point0)
        actor_list.append(vehicle)

        vehicle.set_autopilot(True)



        # camera_bp = blueprint_library.find('sensor.camera.rgb')
        #camera_bp = blueprint_library.find('sensor.camera.semantic_segmentation')
        camera_bp = blueprint_library.find('sensor.camera.instance_segmentation')
        # camera_bp = blueprint_library.find('sensor.camera.depth')
        # camera_bp = blueprint_library.find('sensor.camera.dvs')

        camera_bp.set_attribute("image_size_x", f"{IM_width}")
        camera_bp.set_attribute("image_size_y", f"{IM_Hight}")
        camera_bp.set_attribute("fov", f"{fov}")

        camera_transform = carla.Transform(carla.Location(x=1.5, z=1.5))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle,
                                   attachment_type=carla.AttachmentType.Rigid)
        actor_list.append(camera)
        print('created %s' % camera.type_id)

        # Now we register the function that will be called each time the sensor
        # receives an image. In this example we are saving the image to disk
        # converting the pixels to gray-scale.
        # cc = carla.ColorConverter.LogarithmicDepth
        camera.listen(lambda image: image.save_to_disk(f'_out/semantic_segmentation/{index}_%06d.png' % image.frame,
                                                       carla.ColorConverter.CityScapesPalette))

        camera_bp = blueprint_library.find('sensor.camera.rgb')
        # camera_bp = blueprint_library.find('sensor.camera.depth')
        camera_bp.set_attribute("image_size_x", f"{IM_width}")
        camera_bp.set_attribute("image_size_y", f"{IM_Hight}")
        camera_bp.set_attribute("fov", f"{fov}")

        camera_transform = carla.Transform(carla.Location(x=1.5, z=1.5))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle,
                                   attachment_type=carla.AttachmentType.Rigid)
        actor_list.append(camera)
        print('created %s' % camera.type_id)

        # Now we register the function that will be called each time the sensor
        # receives an image. In this example we are saving the image to disk
        # converting the pixels to gray-scale.
        # cc = carla.ColorConverter.LogarithmicDepth
        camera.listen(lambda image: image.save_to_disk(f'_out/rgb/{index}_%06d.png' % image.frame))

        camera_bp = blueprint_library.find('sensor.camera.depth')
        camera_bp.set_attribute("image_size_x", f"{IM_width}")
        camera_bp.set_attribute("image_size_y", f"{IM_Hight}")
        camera_bp.set_attribute("fov", f"{fov}")

        camera_transform = carla.Transform(carla.Location(x=1.5, z=1))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle,
                                   attachment_type=carla.AttachmentType.Rigid)
        actor_list.append(camera)
        print('created %s' % camera.type_id)

        # Now we register the function that will be called each time the sensor
        # receives an image. In this example we are saving the image to disk
        # converting the pixels to gray-scale.
        # cc = carla.ColorConverter.LogarithmicDepth
        camera.listen(lambda image: image.save_to_disk(f'_out/depth/{index}_%06d.png' % image.frame))

        # Let's add now a "depth" camera attached to the vehicle. Note that the
        # transform we give here is now relative to the vehicle.

        traffic_manager = client.get_trafficmanager(args.tm_port)
        traffic_manager.set_global_distance_to_leading_vehicle(2.5)
        if args.respawn:
            traffic_manager.set_respawn_dormant_vehicles(True)
        if args.hybrid:
            traffic_manager.set_hybrid_physics_mode(True)
            traffic_manager.set_hybrid_physics_radius(70.0)
        if args.seed is not None:
            traffic_manager.set_random_device_seed(args.seed)

        settings = world.get_settings()
        if not args.asynch:
            traffic_manager.set_synchronous_mode(True)
            if not settings.synchronous_mode:
                synchronous_master = True
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.05
            else:
                synchronous_master = False
        else:
            print("You are currently in asynchronous mode. If this is a traffic simulation, \
            you could experience some issues. If it's not working correctly, switch to synchronous \
            mode by using traffic_manager.set_synchronous_mode(True)")

        if args.no_rendering:
            settings.no_rendering_mode = True
        world.apply_settings(settings)

        blueprints = get_actor_blueprints(world, args.filterv, args.generationv)
        blueprintsWalkers = get_actor_blueprints(world, args.filterw, args.generationw)

        if args.safe:
            blueprints = [x for x in blueprints if int(x.get_attribute('number_of_wheels')) == 4]
            blueprints = [x for x in blueprints if not x.id.endswith('microlino')]
            blueprints = [x for x in blueprints if not x.id.endswith('carlacola')]
            blueprints = [x for x in blueprints if not x.id.endswith('cybertruck')]
            blueprints = [x for x in blueprints if not x.id.endswith('t2')]
            blueprints = [x for x in blueprints if not x.id.endswith('sprinter')]
            blueprints = [x for x in blueprints if not x.id.endswith('firetruck')]
            blueprints = [x for x in blueprints if not x.id.endswith('ambulance')]

        blueprints = sorted(blueprints, key=lambda bp: bp.id)

        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points)

        if args.number_of_vehicles < number_of_spawn_points:
            random.shuffle(spawn_points)
        elif args.number_of_vehicles > number_of_spawn_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, args.number_of_vehicles, number_of_spawn_points)
            args.number_of_vehicles = number_of_spawn_points

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        # --------------
        # Spawn vehicles
        # --------------
        batch = []
        hero = args.hero
        for n, transform in enumerate(spawn_points):
            if n >= args.number_of_vehicles:
                break
            blueprint = random.choice(blueprints)
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            if hero:
                blueprint.set_attribute('role_name', 'hero')
                hero = False
            else:
                blueprint.set_attribute('role_name', 'autopilot')

            # spawn the cars and set their autopilot and light state all together
            batch.append(SpawnActor(blueprint, transform)
                .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                logging.error(response.error)
            else:
                vehicles_list.append(response.actor_id)

        # Set automatic vehicle lights update if specified
        if args.car_lights_on:
            all_vehicle_actors = world.get_actors(vehicles_list)
            for actor in all_vehicle_actors:
                traffic_manager.update_vehicle_lights(actor, True)

        # -------------
        # Spawn Walkers
        # -------------
        # some settings
        percentagePedestriansRunning = 0.0      # how many pedestrians will run
        percentagePedestriansCrossing = 0.0     # how many pedestrians will walk through the road
        if args.seedw:
            world.set_pedestrians_seed(args.seedw)
            random.seed(args.seedw)
        # 1. take all the random locations to spawn
        spawn_points = []
        for i in range(args.number_of_walkers):
            spawn_point = carla.Transform()
            loc = world.get_random_location_from_navigation()
            if (loc != None):
                spawn_point.location = loc
                spawn_points.append(spawn_point)
        # 2. we spawn the walker object
        batch = []
        walker_speed = []
        for spawn_point in spawn_points:
            walker_bp = random.choice(blueprintsWalkers)
            # set as not invincible
            if walker_bp.has_attribute('is_invincible'):
                walker_bp.set_attribute('is_invincible', 'false')
            # set the max speed
            if walker_bp.has_attribute('speed'):
                if (random.random() > percentagePedestriansRunning):
                    # walking
                    walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
                else:
                    # running
                    walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
            else:
                print("Walker has no speed")
                walker_speed.append(0.0)
            batch.append(SpawnActor(walker_bp, spawn_point))
        results = client.apply_batch_sync(batch, True)
        walker_speed2 = []
        for i in range(len(results)):
            if results[i].error:
                logging.error(results[i].error)
            else:
                walkers_list.append({"id": results[i].actor_id})
                walker_speed2.append(walker_speed[i])
        walker_speed = walker_speed2
        # 3. we spawn the walker controller
        batch = []
        walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
        for i in range(len(walkers_list)):
            batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))
        results = client.apply_batch_sync(batch, True)
        for i in range(len(results)):
            if results[i].error:
                logging.error(results[i].error)
            else:
                walkers_list[i]["con"] = results[i].actor_id
        # 4. we put together the walkers and controllers id to get the objects from their id
        for i in range(len(walkers_list)):
            all_id.append(walkers_list[i]["con"])
            all_id.append(walkers_list[i]["id"])
        all_actors = world.get_actors(all_id)

        # wait for a tick to ensure client receives the last transform of the walkers we have just created
        if args.asynch or not synchronous_master:
            world.wait_for_tick()
        else:
            world.tick()

        # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
        # set how many pedestrians can cross the road
        world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
        for i in range(0, len(all_id), 2):
            # start walker
            all_actors[i].start()
            # set walk to random point
            all_actors[i].go_to_location(world.get_random_location_from_navigation())
            # max speed
            all_actors[i].set_max_speed(float(walker_speed[int(i/2)]))

        print('spawned %d vehicles and %d walkers, press Ctrl+C to exit.' % (len(vehicles_list), len(walkers_list)))

        # Example of how to use Traffic Manager parameters
        traffic_manager.global_percentage_speed_difference(30.0)

        while True:
            if not args.asynch and synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()

    finally:

        print('destroying actors')
        # camera.destroy()
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('done.')

        if not args.asynch and synchronous_master:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)

        print('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        # stop walker controllers (list is [controller, actor, controller, actor ...])
        for i in range(0, len(all_id), 2):
            all_actors[i].stop()

        print('\ndestroying %d walkers' % len(walkers_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

        time.sleep(0.5)





if __name__ == '__main__':

    print("#######################################################################")

    out_rgp = f'./_out/rgb'
    out_semantic = f'./_out/semantic_segmentation'
    out_depth = f'./_out/depth'


    i =5

    rgb_target = "/home/aitester/Datasets/Carla/rgb"
    semantic_target = "/home/aitester/Datasets/Carla/semantic_segmentation"
    depth_target = "/home/aitester/Datasets/Carla/depth"

    if not os.path.exists(rgb_target):
        os.makedirs(rgb_target)

    if not os.path.exists(semantic_target):
        os.makedirs(semantic_target)

    if not os.path.exists(depth_target):
        os.makedirs(depth_target)

    targetFilels = 31448
    allOk = False
    while not allOk:
        i = i + 1
        try:
            main(i)

            filelist_rgp = [file for file in os.listdir(out_rgp)]
            #print(filelist_rgp)

            for file in filelist_rgp:
                path1 = os.path.join(out_semantic, file)
                path2 = os.path.join(out_depth, file)
                if not ( os.path.exists(path1) and os.path.exists(path2) ) :
                    os.remove(os.path.join(out_rgp, file))

            filelist_semantic = [file for file in os.listdir(out_semantic)]
            for file in filelist_semantic:
                path1 = os.path.join(out_rgp, file)
                path2 = os.path.join(out_depth, file)
                if not ( os.path.exists(path1) and os.path.exists(path2) ):
                    os.remove(os.path.join(out_semantic, file))


            filelist_depth = [file for file in os.listdir(out_depth)]
            for file in filelist_depth:
                path1 = os.path.join(out_rgp, file)
                path2 = os.path.join(out_semantic, file)
                if not ( os.path.exists(path1) and os.path.exists(path2) ):
                    os.remove(os.path.join(out_depth, file))

            rand_str = ''.join(random.choice(string.ascii_letters) for i in range(5))

            filelist_rgp = [file for file in os.listdir(out_rgp)]
            for file in filelist_rgp:
                current = os.path.join(out_rgp, file)
                destination = os.path.join(rgb_target, file)
                if os.path.isfile(destination):
                    destination = os.path.join(rgb_target, rand_str + file)

                shutil.move(current, destination)

            filelist_semantic = [file for file in os.listdir(out_semantic)]
            for file in filelist_semantic:
                current = os.path.join(out_semantic, file)
                destination = os.path.join(semantic_target, file)
                if os.path.isfile(destination):
                    destination = os.path.join(semantic_target, rand_str + file)

                shutil.move(current, destination)

            filelist_depth = [file for file in os.listdir(out_depth)]
            for file in filelist_depth:
                print(file)
                current = os.path.join(out_depth, file)
                destination = os.path.join(depth_target, file)
                if os.path.isfile(destination):
                    destination = os.path.join(depth_target, rand_str + file)

                shutil.move(current, destination)

            if len(os.listdir(rgb_target)) >= targetFilels:
                allOk = True
                break
        except:
            print("end")