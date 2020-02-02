# James Clair, 000847594
import copy
import datetime

import LoadData
import Model
import ShortestPath


def get_formatted_time(time):
    hh = int(time)
    mm = (time * 60) % 60
    ss = (time * 3600) % 60
    return "%d:%02d:%02d" % (hh, mm, ss)


def get_hours_float(time):
    times = []

    for x in time.split(':'):
        times.append(int(x))

    time = datetime.time(times[0], times[1], times[2])
    return float(time.hour + time.minute / 60 + time.second / 3600)


def find_closest_location(delivery_queue):
    closest_distance = float('inf')
    smallest = None
    for i in range(0, len(delivery_queue)):
        print('location:', delivery_queue[i].location.label)
        print('distance:', delivery_queue[i].location.distance)
        if delivery_queue[i].location.distance < closest_distance:
            smallest = i
            closest_distance = delivery_queue[i].location.distance
    if smallest is not None:
        return delivery_queue[smallest].location
    else:
        return None


def check_status(current_time, package_list, hub):
    print()
    packages_by_status = hub.get_packages_by_status(package_list)
    if ((get_hours_float('8:35:00') <= current_time <= get_hours_float('9:25:00') and hub.count == 0) or (
            get_hours_float('9:35:00') <= current_time <= get_hours_float('10:25:00') and hub.count == 1) or (
            get_hours_float('12:03:00') <= current_time <= get_hours_float('13:12:00') and hub.count == 2)):
        print('*** {0} Status Check ***'.format(get_formatted_time(current_time)))
        print()
        print('loaded: ', end="")
        if packages_by_status.read('loaded') is not None:
            for package in packages_by_status.read('loaded'):
                print(package.package_id, end=", ")
        print()
        print('delivered: ', end="")
        for package in packages_by_status.read('delivered'):
            print(package.package_id, end=", ")
        hub.count = hub.count + 1
    print()
    print()


def deliver_package(package, time):
    package.arrival_time = time
    package.delivery_status = 'delivered'


def main():
    package_list = LoadData.load_packages()
    distance_graph = LoadData.load_distances()

    hub = Model.Hub()
    truck_1 = Model.Truck(1, hub.drivers[0])
    truck_2 = Model.Truck(2, hub.drivers[1])
    truck_3 = Model.Truck(3)  # Driver assigned once first truck returns.
    trucks = [truck_1, truck_2, truck_3]

    # Load packages with special notes
    original_list = package_list.copy()
    for package in original_list:
        if package.special_note != "":
            note_parts = package.special_note.split(' ')
            print(note_parts[0])
            if note_parts[0] == "Delayed" or note_parts[0] == "Wrong":
                package.delayed = True
                if truck_2.load_on_truck(package):
                    package_list.remove(package)
            elif note_parts[-2] == 'truck':
                if note_parts[-1] == '1':
                    if truck_1.load_on_truck(package):
                        package_list.remove(package)
                elif note_parts[-1] == '2':
                    if truck_2.load_on_truck(package):
                        package_list.remove(package)
                elif note_parts[-1] == '3':
                    if truck_3.load_on_truck(package):
                        package_list.remove(package)
            else:
                # print(note_parts[0])
                package.peer_packages.append(note_parts[-2][:-1])
                package.peer_packages.append(note_parts[-1])
                if truck_1.load_on_truck(package):
                    package_list.remove(package)
                # print('Peer packages for {0} are: '.format(package.delivery_address))
                # for e in package.peer_packages:
                # print(e)
                for p2 in package_list:
                    if p2.package_id in package.peer_packages and p2.delivery_status != 'loaded':
                        if truck_1.load_on_truck(p2):
                            package_list.remove(p2)
        else:
            if package.delivery_deadline != 'EOD' and package.delivery_status != 'loaded':
                if truck_1.load_on_truck(package):
                    package_list.remove(package)

    truck_1_packages_by_address = hub.get_packages_by_address(truck_1.delivery_queue)
    truck_2_packages_by_address = hub.get_packages_by_address(truck_2.delivery_queue)
    truck_3_packages_by_address = hub.get_packages_by_address(truck_3.delivery_queue)
    truck_1_packages_by_zip = hub.get_packages_by_zip(truck_1.delivery_queue)
    truck_2_packages_by_zip = hub.get_packages_by_zip(truck_2.delivery_queue)
    truck_3_packages_by_zip = hub.get_packages_by_zip(truck_3.delivery_queue)
    truck_1_packages_by_city = hub.get_packages_by_city(truck_1.delivery_queue)
    truck_2_packages_by_city = hub.get_packages_by_city(truck_2.delivery_queue)
    truck_3_packages_by_city = hub.get_packages_by_city(truck_3.delivery_queue)

    for package in package_list:
        if truck_1_packages_by_address.read(package.delivery_address) is not None:
            if truck_1.load_on_truck(package):
                continue
        if truck_2_packages_by_address.read(package.delivery_address) is not None:
            if truck_2.load_on_truck(package):
                continue
        if truck_3_packages_by_address.read(package.delivery_address) is not None:
            if truck_3.load_on_truck(package):
                continue
        if truck_1_packages_by_zip.read(package.delivery_zip) is not None:
            if truck_1.load_on_truck(package):
                continue
        if truck_2_packages_by_zip.read(package.delivery_zip) is not None:
            if truck_2.load_on_truck(package):
                continue
        if truck_3_packages_by_zip.read(package.delivery_zip) is not None:
            if truck_3.load_on_truck(package):
                continue
        if truck_1_packages_by_city.read(package.delivery_city) is not None:
            if truck_1.load_on_truck(package):
                continue
        if truck_2_packages_by_city.read(package.delivery_city) is not None:
            if truck_2.load_on_truck(package):
                continue
        if truck_3_packages_by_city.read(package.delivery_city) is not None:
            if truck_3.load_on_truck(package):
                continue
        else:
            if truck_1.load_on_truck(package):
                continue
            if truck_2.load_on_truck(package):
                continue
            if truck_3.load_on_truck(package):
                continue
            else:
                print('Unable to load package on truck')

    for truck in trucks:
        print('#' * 118)
        print('# Truck {0}:'.format(truck.truck_id))
        print('# Truck {0} delivery queue length: {1}'.format(truck.truck_id, len(truck.delivery_queue)))
        print('#' * 118)
        for package in truck.delivery_queue:
            print(package)

    # Deliver packages
    last_location = distance_graph.hub_vertex
    truck_1.start_time = hub.start_time
    truck_2.start_time = get_hours_float('09:05:00')
    for truck in trucks:
        # set the current time
        ShortestPath.dijkstra_shortest_path(distance_graph, last_location)
        if truck.truck_id == 3:
            truck.start_time = min(truck_1.finish_time, truck_2.finish_time)
            truck.start_time = max(truck.start_time, get_hours_float('10:20:00'))
            # hub.wrong_address[0].delivery_address = '410 S State St.'
            # for v in distance_graph.adjacency_list:
            #     if v.label == hub.wrong_address[0].delivery_address:
            #         hub.wrong_address[0].location = v
            # hub.wrong_address[0].delivery_city = 'Salt Lake City'
            # hub.wrong_address[0].delivery_zip = '84111'
            # truck_3.load_on_truck(hub.wrong_address[0])
        print('# Truck {0} start: {1}'.format(truck.truck_id, truck.start_time))
        current_time = truck.start_time

        # Deliver packages with a Deadline
        count = 0
        deadline_packages = []
        for package in truck.delivery_queue:
            if package.delivery_deadline != 'EOD':
                deadline_packages.append(package)

        current_location = find_closest_location(deadline_packages)
        while len(deadline_packages) > 0:
            print('last_total: {0} '.format(hub.total_distance), end='')
            print('+ distance from last: {0} = '.format(current_location.distance), end='')
            hub.total_distance += current_location.distance
            print('new_total: {0}'.format(hub.total_distance))

            print('last_truck_distance: {0} '.format(truck.distance), end='')
            print('+ distance from last: {0} = '.format(current_location.distance), end='')
            truck.distance += current_location.distance
            print('new_truck_distance: {0}'.format(truck.distance))
            current_time = truck.start_time + (truck.distance / 18)
            print('current_time: ', current_time)

            packages_by_address = hub.get_packages_by_address(truck.delivery_queue)
            for package in packages_by_address.read(current_location.label):
                deliver_package(package, current_time)
                if package in deadline_packages:
                    deadline_packages.remove(package)
                    # print(deadline_packages)
                truck.delivery_queue.remove(package)
                print(package)
                count += 1

            # Run status check
            check_status(current_time, original_list, hub)

            last_location = current_location
            # Run dijkstras
            for v in distance_graph.adjacency_list:
                v.distance = float('inf')
                v.predecessor = None
            ShortestPath.dijkstra_shortest_path(distance_graph, current_location)

            # Update next location
            current_location = find_closest_location(deadline_packages)

            # Update the truck's path
            truck.paths.append(ShortestPath.get_shortest_path(last_location, current_location))

        # first location
        current_location = find_closest_location(truck.delivery_queue)

        # Deliveries
        last_location = distance_graph.hub_vertex
        while len(truck.delivery_queue) > 0:
            # Deliver packages for location
            print('last_total: {0} '.format(hub.total_distance), end='')
            print('+ distance from last: {0} = '.format(current_location.distance), end='')
            hub.total_distance += current_location.distance
            print('new_total: {0}'.format(hub.total_distance))

            print('last_truck_distance: {0} '.format(truck.distance), end='')
            print('+ distance from last: {0} = '.format(current_location.distance), end='')
            truck.distance += current_location.distance
            print('new_truck_distance: {0}'.format(truck.distance))
            current_time = truck.start_time + (truck.distance / 18)
            print('current_time: ', current_time)
            print('current_location.label: ', current_location.label)

            packages_by_address = hub.get_packages_by_address(truck.delivery_queue)
            for package in packages_by_address.read(current_location.label):
                deliver_package(package, current_time)
                truck.delivery_queue.remove(package)
                print(package)
                count += 1



            # Run status check
            check_status(current_time, original_list, hub)

            last_location = copy.deepcopy(current_location)
            # Run dijkstras
            for v in distance_graph.adjacency_list:
                v.distance = float('inf')
                v.predecessor = None
            ShortestPath.dijkstra_shortest_path(distance_graph, current_location)

            # Update next location
            current_location = find_closest_location(truck.delivery_queue)
            # print('last_location:', last_location.label)
            # if current_location is not None:
            #     print('current_location:', current_location.label)
            # print('running shortest path')
            truck.paths.append(ShortestPath.get_shortest_path(last_location, current_location))

        # Return the truck to the hub
        ShortestPath.dijkstra_shortest_path(distance_graph, last_location)
        truck.paths.append(ShortestPath.get_shortest_path(last_location, distance_graph.hub_vertex))
        truck.distance += distance_graph.hub_vertex.distance
        hub.total_distance += distance_graph.hub_vertex.distance
        truck.finish_time = truck.start_time + (truck.distance / 18)
        truck.packages_delivered = count

        # Run status check
        check_status(truck.finish_time, original_list, hub)

        print(truck)

    hub.finish_time = max(truck_1.finish_time, truck_2.finish_time, truck_3.finish_time)
    hub.packages_delivered = truck_1.packages_delivered + truck_2.packages_delivered + truck_3.packages_delivered

    for truck in trucks:
        print('Truck {0} path:'.format(truck.truck_id))
        for path in truck.paths:
            print(path)

    print('Total distance of all trucks: {0:.2f}'.format(hub.total_distance))
    print('All packages delivered at: {0}'.format(get_formatted_time(hub.finish_time)))
    print('Total packages delivered: ', hub.packages_delivered)


if __name__ == "__main__":
    main()
