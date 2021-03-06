class Configurations:
    config_values = {}  # dictionary containing all configs
    DEFAULT_CONFIG_FNAME = "config.json" # default config filename

    @staticmethod
    def setRuntimeConfigs(filename = DEFAULT_CONFIG_FNAME):
        # sets all hardcoded values in DEFAULT_CONFIG_VALUES
        # if the designated config file is not detected, create one
        # and populate with default configs
        # If it exists, read from it

        Configurations.config_values["runtime_script"] = "script.txt"
        Configurations.config_values["node_add_if_exists"] = True
        Configurations.config_values["connection_add_if_exists"] = True
        Configurations.loadConfigFile(filename)
        Configurations.writeConfigFile(filename)

    @staticmethod
    def loadConfigFile(filename = DEFAULT_CONFIG_FNAME):
        # loads configs from given file, if it exists
        import os.path
        if os.path.exists(filename):
            with open(filename, 'r') as infile:
                Configurations.config_values = json.load(infile)


    @staticmethod
    def writeConfigFile(filename=DEFAULT_CONFIG_FNAME):
        # writes current configs to given file
        with open(filename, 'w') as outfile:
            json.dump(Configurations.config_values, outfile, indent=4, sort_keys=True)

class KeyGenerator:
    # Generator class that keeps track of automatic namings
    # For instance, creates "Connection1","Connection2".... given "Connection" as a starting string
    name_to_count = {}  # keeps track of autonumber for each name

    @staticmethod
    def getNextName(generatorname = "", existing_keys = []):
        # Generates next key name in sequence that does not exist within existing key list
        # If sequence does not exist, create one
        return_string = ""
        while True:
            if generatorname not in KeyGenerator.name_to_count.keys(): # create new sequence
                KeyGenerator.name_to_count[generatorname] = 0
            possible_name = generatorname + str(KeyGenerator.name_to_count[generatorname])
            if possible_name not in existing_keys:
                return possible_name
            else:
                KeyGenerator.name_to_count[generatorname] = KeyGenerator.name_to_count[generatorname] + 1

class Supergraph:
    keylist = []          # list of keys. Prevents a connection, graph and a node having the same name
    graphlist = dict()        # dictionary maintaining a graph name to graph pointer conversion
    nodelist = dict()         # dictionary maintaining a node name to node pointer conversion
    connectionlist = dict()   # dictionary maintaining a connection name to connection pointer conversion
    nodeconnectionlist = dict()    # maintains a dictionary of nodes to Sets of connection keys

    supergraphdata = {}   # dictionary maintaining a variable name to variable data conversion

    @staticmethod
    def getNodeConnectionList():
        return Supergraph.nodeconnectionlist

    @staticmethod
    def getKeyList():
        return Supergraph.keylist

    @staticmethod
    def verifyKeys(keylist):
        # Will remove any names from list that don't point to anything
        returnlist = []
        for key in keylist:
            if key in Supergraph.keylist:
                returnlist.append(key)  # add valid name to list
        return returnlist

    @staticmethod
    def getPointerData(pointers = [], this = ""):
        # Pulls data from supergraph when given a pointer such as NODE.DATA
        if len(pointers) == 1:
            if pointers[0] == "THIS":
                if this == "":
                    raise Exception("Keyword THIS does not currently reference something")
                reference = this
            else:
                reference = pointers[0]
            
            if reference in Supergraph.nodelist.keys():
                return reference
            elif reference in Supergraph.connectionlist.keys():
                return reference
            elif reference in Supergraph.graphlist.keys():
                return reference
        elif len(pointers) == 2:
            if pointers[0] == "THIS":
                if this == "":
                    raise Exception("Keyword THIS does not currently reference something")
                reference = this
            else:
                reference = pointers[0]
            if reference in Supergraph.nodelist.keys():
                data = Supergraph.getNodeData([reference], pointers[1])
                if len(data) == 0:
                    return None
                else:
                    return data[0]
            if reference in Supergraph.connectionlist.keys():
                data = Supergraph.getConnectionData([reference], pointers[1])
                if len(data) == 0:
                    return None
                else:
                    return data[0]
            # elif reference in Supergraph.connectionlist.keys():
            #     return Supergraph.getConnectionData([reference], pointers[1])
            # elif reference in Supergraph.graphlist.keys():
            #     return Supergraph.getGraphData([reference], pointers[1])
        return None

    @staticmethod
    def addData( varname,  vardata):
        if (varname not in Supergraph.supergraphdata) and varname != "name":
            Supergraph.supergraphdata[varname] = vardata

    @staticmethod
    def getData( varname):
        # gets type and value of requested variable,  none if it doesn't exist
        if varname in Supergraph.supergraphdata:
            # print "RETURNING " + Supergraph.name + ": "+str([Supergraph.nodedatatype[varname], Supergraph.nodedata[varname]])
            return Supergraph.supergraphdata[varname]
        return None

    @staticmethod
    def removeData( varname):
        if varname in Supergraph.supergraphdata:
            del Supergraph.supergraphdata[varname]
            del Supergraph.supergraphdatatype[varname]

    @staticmethod
    def addGraph( graphname,  nodekeys = [],  connectionkeys = []):
        # Adds a graph to the database
        if graphname not in Supergraph.graphlist and graphname not in Supergraph.keylist:
            Supergraph.graphlist[graphname] = Graph( graphname,  nodekeys,  connectionkeys)
            Supergraph.keylist.append(graphname)

    @staticmethod
    def removeGraphs( graphnames):
        verifiedgraphs = Supergraph.verifyGraphNames(graphnames)     # get list of graphs from keys
        for graphname in verifiedgraphs:
            del Supergraph.graphlist[graphname]
            Supergraph.keylist.remove(graphname)

    @staticmethod
    def getAllGraphKeys():
        #  Lists names of all existing graphs
        return Supergraph.graphlist.keys()

    @staticmethod
    def printGraphList():
        #  Lists names of all existing graphs
        print(Supergraph.graphlist.keys())

    @staticmethod
    def verifyGraphNames( graphnames = []):
        # Will remove any names from list that don't point to anything
        returnlist = []
        for name in graphnames:
            if name in Supergraph.graphlist.keys():
                returnlist.append(name) # add valid name to list
        return returnlist

    @staticmethod
    def namesToGraphs( graphnames = []):
        # Converts a list of a keys to graph pointers
        returnlist = []
        for i in graphnames:
            if graphnames[i] in Supergraph.graphlist:
                returnlist.append(Supergraph.graphlist[graphnames[i]])
        return returnlist

    @staticmethod
    def addNode(nodename, nodedata = {}, add_if_exists = False):
        assert type(nodename) is str
        assert type(nodedata) is dict

        #  Adds a node to the database. Returns True if successful
        if nodename not in Supergraph.nodelist and nodename not in Supergraph.keylist:
            Supergraph.nodelist[nodename] = Node(nodename)
            Supergraph.nodeconnectionlist[nodename] = set()
            Supergraph.keylist.append(nodename)
            return nodename
        else:
            if add_if_exists or Configurations.config_values["node_add_if_exists"]:
                new_node = KeyGenerator.getNextName(nodename, Supergraph.getAllNodeKeys())
                Supergraph.nodelist[new_node] = Node(new_node)
                Supergraph.nodeconnectionlist[new_node] = set()
                Supergraph.keylist.append(new_node)
                return new_node
        return nodename # already exists in graph if everything fails

    @staticmethod
    def addNodes(nodenames = {}, nodedata={}, add_if_exists = False):
        assert type(nodenames) in [list,set]
        assert type(nodedata) is dict

        returned_nodes = set()
        for nodename in nodenames:
            returned_nodes.add(Supergraph.addNode(nodename,nodedata, add_if_exists))

        return returned_nodes

    @staticmethod
    def removeNodes( nodenames):
        # Removes a list of nodes from the database
        verifiednodes = Supergraph.verifyNodeNames(nodenames)     # get list of nodes from keys
        for nodename in verifiednodes:
            del Supergraph.nodelist[nodename]
            del Supergraph.nodeconnectionlist[nodename]
            Supergraph.keylist.remove(nodename)

    @staticmethod
    def getAllNodeKeys():
        # lists the node keys
        return Supergraph.nodelist.keys()

    @staticmethod
    def printNodeList():
        # lists the node keys
        print(Supergraph.nodelist.keys())

    @staticmethod
    def verifyNodeNames( nodenames = []):
        # Will remove any names from list that don't point to anything
        returnlist = []
        for name in nodenames:
            if name in Supergraph.nodelist.keys():
                returnlist.append(name) # add valid name to list
        return returnlist

    @staticmethod
    def namesToNodes( nodenames = []):
        # Converts a list of a keys to node pointers
        #  Will remove any names from list that don't point to anything
        returnlist = []
        names = Supergraph.verifyNodeNames(nodenames)
        for i in names:
            returnlist.append(Supergraph.nodelist[i]) # get pointer from node list
        return returnlist

    @staticmethod
    def getNodeNeighbors(nodekeys = []):
        # Get neighbors directly connected to a list of nodes
        return_list = set()
        for node in nodekeys:
            for connection in Supergraph.namesToConnections(Supergraph.nodeconnectionlist[node]):
                neighbor = Connection.getEndPoint(connection,node)
                if neighbor is not None:
                    return_list.add(neighbor)

        return list(return_list)

    @staticmethod
    def addNodeData( nodenames,  varname,  vardata):
        #  Adds data to a list of nodes
        nodes = Supergraph.namesToNodes(nodenames)  #  get list of nodes from keys
        for i in nodes:
            Node.addNodeData(i,  varname,  vardata)

    @staticmethod
    def getNodeDegrees(nodenames = [], degree = "in"):
        # Returns the degrees or indegrees for a list of node keys
        assert degree in ["in","out"], AttributeError
        verified_nodes = Supergraph.namesToNodes(nodenames)  # get list of nodes from keys
        returnlist = []
        for node in verified_nodes:
            returnlist.append(Node.getNodeDegree(node,degree))
        return returnlist


    @staticmethod
    def getNodeData( nodenames,  varname):
        # Gets requested variable from a list of nodes.
        # Returns a list containing the values
        # Won't append data if it doesn't exist for that node
        nodes = Supergraph.namesToNodes(nodenames)  #  get list of nodes from keys
        returnlist = []
        for i in nodes:
            value = Node.getNodeData(i,  varname)   # get the array containing the type and value of the data
            if value is not None:
                returnlist.append(value)
        return returnlist

    @staticmethod
    def removeNodeData( nodenames,  varname):
        #  Removes data from a list of nodes
        nodes = Supergraph.namesToNodes(nodenames)  #  get list of nodes from keys
        for node in nodes:
            Node.removeNodeData(nodes[node],  varname)

    @staticmethod
    def addConnection( connectionname,  leftname,  rightname, direction = "both", add_if_exists = False):
        # creates a connection in the database. Returns true if successful, false if not

        assert type(connectionname) is str
        assert type(leftname) is str
        assert type(rightname) is str

        # Check if left and right keys in database, otherwise it fails
        if leftname not in Supergraph.nodelist.keys():
            return False
        if rightname not in Supergraph.nodelist.keys():
            return False

        if connectionname not in Supergraph.connectionlist and connectionname not in Supergraph.keylist:
            Supergraph.connectionlist[connectionname] = Connection(connectionname, leftname,  rightname, direction)
            Supergraph.nodeconnectionlist[leftname].add(connectionname)
            Supergraph.nodeconnectionlist[rightname].add(connectionname)
            Supergraph.keylist.append(connectionname)
            return connectionname
        else:
            if add_if_exists or Configurations.config_values["connection_add_if_exists"]:
                new_conn = KeyGenerator.getNextName(connectionname)
                Supergraph.connectionlist[new_conn] = Connection(new_conn, leftname,  rightname, direction)
                Supergraph.nodeconnectionlist[leftname].add(new_conn)
                Supergraph.nodeconnectionlist[rightname].add(new_conn)
                Supergraph.keylist.append(connectionname)
                return new_conn
        return connectionname


    @staticmethod
    def addConnections( leftnames,  rightnames, direction = 'both', generator = "Connection", prevent_recursive = False):
        # Adds connections to the database
        # Will connect every node from left side to right side,  resulting in L * R connections
        assert direction in ["both","right"]

        return_connections = set()

        verifiedleftnames = Supergraph.verifyNodeNames(leftnames)
        verifiedrightnames = Supergraph.verifyNodeNames(rightnames)
        for left in verifiedleftnames:
            for right in verifiedrightnames:
                if left != right or not prevent_recursive:
                    connectionname = KeyGenerator.getNextName(generator, Supergraph.getAllConnectionKeys())
                    return_connections.add(Supergraph.addConnection(connectionname, left, right, direction))

        return return_connections

    @staticmethod
    def removeConnections(connectionnames):
        # removes the specified connections,  if they exist
        for connectionkey in list(connectionnames):
            if connectionkey in Supergraph.connectionlist.keys():
                # remove references to this connection for the left and right nodes it connects
                c = Supergraph.connectionlist[connectionkey]
                leftkey = Connection.getConnectionData(c,"leftkey")
                rightkey = Connection.getConnectionData(c,"rightkey")
                if leftkey in Supergraph.nodeconnectionlist:
                    if connectionkey in Supergraph.nodeconnectionlist[leftkey]:
                        Supergraph.nodeconnectionlist[leftkey].remove(connectionkey)
                if rightkey in Supergraph.nodeconnectionlist:
                    if connectionkey in Supergraph.nodeconnectionlist[rightkey]:
                        Supergraph.nodeconnectionlist[rightkey].remove(connectionkey)
                # remove connection
                del Supergraph.connectionlist[connectionkey]
                Supergraph.keylist.remove(connectionkey)

    @staticmethod
    def getAllConnectionKeys():
        # lists the node keys
        return Supergraph.connectionlist.keys()

    @staticmethod
    def printConnectionList():
        # lists the node keys
        print(Supergraph.connectionlist.keys())

    @staticmethod
    def getNextConnectionName():
        # Used for automatically naming connections
        # Will update id counter to make it as up to date as possible
        connectname = Supergraph.connectionidprefix + str(Supergraph.connectionidsuffix)
        while (connectname in Supergraph.connectionlist) or (connectname in Supergraph.keylist):
            Supergraph.connectionidsuffix += 1
            connectname = Supergraph.connectionidprefix + str(Supergraph.connectionidsuffix)
        return connectname

    @staticmethod
    def verifyConnectionNames( connectionnames = []):
        # Will remove any names from list that don't point to anything
        returnlist = []
        for name in connectionnames:
            if name in Supergraph.connectionlist.keys():
                returnlist.append(name) #append valid name to list
        return returnlist

    @staticmethod
    def namesToConnections( connectionnames = []):
        # Converts a list of a keys to connection pointers
        #  Will remove any names from list that don't point to anything
        returnlist = []
        verifiednames = Supergraph.verifyConnectionNames(connectionnames)
        for name in verifiednames:
            returnlist.append(Supergraph.connectionlist[name]) # get pointer from node list
        return returnlist

    @staticmethod
    def addConnectionData( connectionnames,  varname,  vardata):
        #  Adds data to a list of connections
        connections = Supergraph.namesToConnections(connectionnames)  #  get list of connections from keys
        for i in connections:
            Connection.addConnectionData(i,  varname,  vardata)

    @staticmethod
    def getConnectionData( connectionnames,  varname):
        # Gets requested variable from a list of nodes.
        # Returns a list containing the values
        # Won't append data if it doesn't exist for that node
        connections = Supergraph.namesToConnections(connectionnames)  # get list of nodes from keys
        returnlist = []
        for i in connections:
            value = Connection.getConnectionData(i, varname)  # get the array containing the type and value of the data
            if value is not None:
                returnlist.append(value)
        return returnlist

    @staticmethod
    def removeConnectionData( connectionnames,  varname):
        #  Removes data from a list of connections
        connections = Supergraph.namesToConnections(connectionnames)  #  get list of connections from keys
        for connection in connections:
            Connection.removeConnectionData(connections[connection],  varname)

    @staticmethod
    def showAllConnections():
        # prints all connections, and their left and right keys
        for connect in Supergraph.connectionlist.values():
            print(connect.name, ": ",connect.leftkey,", ",connect.rightkey)

    @staticmethod
    def getNodeConnections(nodekeys=[],connectionkeys = []):
        # gets all connection keys that belong to the given list of nodes
        # Will restrain the search to a list of connections
        # maintains direction of connections

        returnlist = set() # is a set to restrict duplicate connections. Converted to list at end
        connections = Supergraph.namesToConnections(connectionkeys)
        for connect in connections:
            leftkey = connect.leftkey
            rightkey = connect.rightkey
            direction = connect.direction
            # check if an endpoint is in given node list, and destination lines up
            if (leftkey in nodekeys) and (direction in ['right','both']):
                returnlist.add(connect.name)
            if (rightkey in nodekeys) and (direction in ['left','both']):
                returnlist.add(connect.name)

        return list(returnlist)

class Graph:
    def __init__(self, name, nodekeys, connectionkeys):
        self.name = name                           # name uniquely identifying the graph
        self.nodekeys = nodekeys                   # list of node keys used in this graph
        self.connectionkeys = connectionkeys       # list of connection keys used in this graph

    # def addConnections(self,connections):
    #     for connection in connections:
    #         if connection in self.connectionkeys:
    #             self.connectionkeys.remove(connection)
    #
    # def getConnections(self):
    #     return self.connectionkeys
    #
    # def removeConnections(self,connections):
    #     for connection in connections:
    #         if connection not in self.connectionkeys:
    #             self.connectionkeys.append(connection)
    #
    # def addNodes(self, nodes):
    #     for node in nodes:
    #         if node not in self.nodekeys:
    #             self.nodekeys.append(node)
    #
    # def getNodes(self):
    #     return self.nodekeys
    #
    # def removeNodes(self,nodes):
    #     for node in nodes:
    #         if node in self.nodekeys:
    #             self.nodekeys.remove(node)

class Node:
    def __init__(self, name):
        self.name = name
        self.nodedata = {}

    def addNodeData(self,  varname,  vardata):
        if varname.lower() != "name":
            self.nodedata[varname] = vardata

    def getNodeData(self,  varname):
        # gets type and value of requested variable,  none if it doesn't exist
        if varname in self.nodedata:
            # print "RETURNING " + self.name + ": "+str([self.nodedatatype[varname], self.nodedata[varname]])
            return self.nodedata[varname]
        if varname.lower() == "name":
            return self.name
        return None

    def removeNodeData(self,  varname):
        if varname in self.nodedata:
            del self.nodedata[varname]

    def getNodeDegree(self,degree = "in"):
        # Counts either the indegree or outdegree of the node

        assert degree in ["in","out"], AttributeError

        degree_count = 0    # count of degree for the node
        c_list = Supergraph.nodeconnectionlist[self.name] # get list of connection keys
        for connectionkey in c_list:
            conn = Supergraph.connectionlist[connectionkey]
            leftkey = Connection.getConnectionData(conn,"leftkey")
            rightkey = Connection.getConnectionData(conn, "rightkey")
            direction = Connection.getConnectionData(conn, "direction")

            # Bidirectional edges count either way for in or outdegree
            if direction == "both":
                degree_count += 1
                continue

            if degree == "in":
                if self.name == rightkey and direction == "right":
                    degree_count += 1
            else:
                if self.name == leftkey and direction == "right":
                    degree_count += 1

        return degree_count

class Connection:
    def __init__(self, name, leftkey, rightkey,
                 direction = "both"): # The endpoint of the connection. Either right for directed, or both for undirected.
        self.name = name   # unique name of the connection used as a key
        assert direction in ['right','both']
        self.connectiondata = {"leftkey": leftkey, "rightkey":rightkey,"direction":direction}  # maintains information about the connection

    def addConnectionData(self,  varname,  vardata):
        if varname.lower() not in ["name","leftkey","rightkey","direction"]:
            self.connectiondata[varname] = vardata

    def getConnectionData(self,  varname):
        # gets type and value of requested variable,  none if it doesn't exist
        if varname in self.connectiondata:
            return self.connectiondata[varname]
        if varname.lower() == "name":
            return self.name
        return None

    def getLeftKey(self):
        return self.connectiondata["leftkey"]

    def getRightKey(self):
        return self.connectiondata["rightkey"]

    def getDirection(self):
        return self.connectiondata["direction"]

    def removeConnectionData(self,  varname):
        if varname in self.connectiondata:
            del self.connectiondata[varname]

    def getEndPoint(self,startpoint):
        # Used to traverse a connection, given the start point
        # If you attempt to go the opposite way from a directed edge, it returns None
        if startpoint not in [self.connectiondata["leftkey"],self.connectiondata["rightkey"]]:
            return None

        if self.connectiondata["direction"] == "both":
            if startpoint == self.connectiondata["leftkey"]:
                return self.connectiondata["rightkey"]
            else:
                return self.connectiondata["leftkey"]
        else:
            if startpoint == self.connectiondata["leftkey"]:
                return self.connectiondata["rightkey"]
            else:
                return None


class GraphCentrality:
    # Adds various methods for computing graph centrality

    @staticmethod
    def pruneConnections(nodes=list(), connections=list()):
        filtered_connections = set()  # set of filtered connection keys
        # add all connections that point somewhere in the subgraph, filtering the ones pointing out of it
        for conn in connections:
            if Supergraph.connectionlist[conn].getLeftKey() in nodes and Supergraph.connectionlist[
                conn].getRightKey() in nodes:
                filtered_connections.add(conn)
        return filtered_connections

    @staticmethod
    def getEigenVectorCentrality(nodes=list(), connections=list(), iteration_count = 50):
        # returns a dict containing the eigenvector centrality for each node in the given subgraph

        from numpy import matrix, dot

        node_to_index = dict()  # quickly convert node keys to their respective index in the matrices
        node_to_weight = dict()  # quickly convert node keys to their weights
        counter = 0
        for node in nodes:
            node_to_index[node] = counter
            node_to_weight[node] = 0
            counter += 1

        # create empty adjacency matrix
        adjacency = list()  # adjacency matrix as a list to be converted to numpy
        for index in range(0,len(nodes)):
            adjacency.append([0] * len(nodes))

        filtered_connections = GraphCentrality.pruneConnections(nodes,connections)

        # get node weights
        for item in filtered_connections:
            conn = Supergraph.namesToConnections([item])[0]
            leftkey = Connection.getLeftKey(conn)
            rightkey = Connection.getRightKey(conn)
            node_to_weight[leftkey] += 1
            if Connection.getDirection(conn) == "both":
                node_to_weight[rightkey] += 1

        # to avoid sinks in directed graphs, nodes with no outbounds link to ALL other nodes
        for node in node_to_weight.keys():
            if node_to_weight[node] == 0:
                for outbound in node_to_weight.keys():
                    if node != outbound:
                        adjacency[node_to_index[node]][node_to_index[outbound]] = 1.0 / max(1,len(nodes) - 1)

        # populate adjacency matrix
        for item in filtered_connections:
            conn = Supergraph.namesToConnections([item])[0]
            leftkey = Connection.getLeftKey(conn)
            rightkey = Connection.getRightKey(conn)

            adjacency[node_to_index[leftkey]][node_to_index[rightkey]] = 1.0 / max(1, node_to_weight[leftkey])

            if Connection.getDirection(conn) == "both":
                adjacency[node_to_index[rightkey]][node_to_index[leftkey]] = 1.0 / max(1, node_to_weight[rightkey])

        # assign each node a starting value for centrality
        centrality = list()
        for node in nodes:
            # centrality.append([1.0 / max(1, len(nodes))])
            centrality.append(1.0 / max(1, len(nodes)))

        # get numpy matrices
        centrality_matrix = matrix(centrality)
        adjacency_matrix = matrix(adjacency)

        # perform matrix multiplication to compute centrality
        for x in range(iteration_count):
            centrality_matrix = dot(centrality_matrix, adjacency_matrix)

        # convert answer to dictionary
        centrality_list = centrality_matrix.tolist()[0]
        eigenvalues = dict()
        for node in nodes:
            eigenvalues[node] = centrality_list[node_to_index[node]]

        return eigenvalues

class PathFinder:
    #Impliments pathfinding algorithms using the Supergraph Database

    @staticmethod
    def getUnweightedAllPairs(nodes=list(), connections=list()):
        # get a 2d dictionary getting path info from all given nodes to all other nodes(if possible) in given subgraph

        node_to_visited_time = dict() # maintains node, to when that node visited another node
        node_to_destination_to_node = dict()  # maintains parent heirarchy in BFS as node_to_parent[node] = (origin node, time)
        time = 0        # current step
        path_count = 0    # number of paths found
        time_to_node_to_new = dict()    # maintains newly discovered nodes at each time step
        time_to_node_to_new[0] = dict() # initialize discovered nodes at time 0

        # get the dictionary of nodes to sets of connection keys
        for node in nodes:
            node_to_visited_time[node] = dict()
            node_to_destination_to_node[node] = dict()
            time_to_node_to_new[0][node] = set()
            node_to_unvisited_nodes = set(nodes)
            node_to_unvisited_nodes.remove(node)

        # add all connections that point somewhere in the subgraph, filtering the ones pointing out of it
        # additionally, begin population of pathing dictionaries
        for conn in connections:
            leftkey = Supergraph.connectionlist[conn].getLeftKey()
            rightkey = Supergraph.connectionlist[conn].getRightKey()
            if leftkey == rightkey:
                continue    # recursive connection, ignore it
            if leftkey in nodes and rightkey in nodes:
                node_to_visited_time[leftkey][rightkey] = 0                 # time of discovery
                node_to_destination_to_node[leftkey][rightkey] = leftkey    # tell the left key the right key is connected using the left
                time_to_node_to_new[0][leftkey].add(rightkey)               # right was discovered at initiazation by left
                path_count += 1
            else:
                continue    # edge points outside of graph; ignore it
            if Supergraph.connectionlist[conn].getDirection() == "both":    # if bidirectional, handle reverse case
                node_to_visited_time[rightkey][leftkey] = 0                 # time of discovery
                node_to_destination_to_node[rightkey][leftkey] = rightkey   # tell the right key the left key is connected using the right
                time_to_node_to_new[0][rightkey].add(leftkey)               # leftkey was discovered at initiazation by right
                path_count += 1

        finished = False    # will exit when no propagation is capable


        while(not finished):
            finished = True # will exit unless propagation occurs on this step
            time_to_node_to_new[time+1] = dict()

            print(time)

            # iterate over all nodes(A) that are scheduled to propagate this timestep
            for node in time_to_node_to_new[time].keys():
                print("\t",node)
                # iterate over the newly discovered nodes(B) for each node(A)
                for last_found_node in time_to_node_to_new[time][node]:
                    # find the nodes(C) that new node(B) has access to that the current node(A) doesn't know about
                    newly_found_nodes = node_to_destination_to_node[last_found_node].keys() - node_to_destination_to_node[node].keys()    # find the nodes the recent node found

                    # Grab the routing info from the B to C and pass it to A
                    for new_node in newly_found_nodes:
                        path_count += 1
                        node_to_visited_time[node][new_node] = time+1       # add discovery time for new node
                        node_to_destination_to_node[node][new_node] = last_found_node
                        # create a new set for node A at future time holding the newest found nodes if it doesn't exist
                        if node not in time_to_node_to_new[time+1].keys():
                            time_to_node_to_new[time + 1][node] = set()
                        time_to_node_to_new[time+1][node].add(new_node)
                        finished = False    # propagation happened, so we won't exit
            time_to_node_to_new.pop(time)
            time += 1


        # # print the propagation of the algorithm
        # for time in time_to_node_to_new.keys():
        #     print(time,time_to_node_to_new[time])

        from time import sleep

        # for node in node_to_destination_to_node.keys():
        #     print(node,node_to_destination_to_node[node])

        print("paths", path_count, "time steps:", time)

        return node_to_destination_to_node  # returns dictionary containing all necessary routing info



    @staticmethod
    def getUnweightedBFS(start_node, nodes=list(), connections=list()):
        # Gets min distances from start node to every other node in subgraph

        from PriorityQueue import PriorityQueue

        assert type(nodes) is list
        assert type(connections) is list

        if start_node not in nodes:
            return None

        unvisited_connections = set()  # set of unvisited connection keys
        node_to_parent = dict()  # maintains parent heirarchy in BFS as node_to_parent[node] = (origin node, connectionkey)
        node_to_dist = dict()  # maintains distance of given node from start

        node_to_connections = dict()  # maintains dict of node key to sets of connection pointers
        conn_queue = PriorityQueue()  # stores priority queue of weighted connections as tuples of (origin node, connection, dest_node)

        # add all connections that point somewhere in the subgraph, filtering the ones pointing out of it
        for conn in connections:
            if Supergraph.connectionlist[conn].getLeftKey() in nodes and Supergraph.connectionlist[
                conn].getRightKey() in nodes:
                unvisited_connections.add(conn)

        # get the dictionary of nodes to sets of connection keys
        for node in nodes:
            node_to_connections[node] = Supergraph.nodeconnectionlist[node].intersection(unvisited_connections)

        # add all the connections from the starting node to the queue
        for conn in node_to_connections[start_node]:
            endpoint = Supergraph.connectionlist[conn].getEndPoint(start_node)
            if endpoint is not None:
                conn_queue.insert(node=(start_node, conn, endpoint), priority=1)

        node_to_dist[start_node] = 0

        while conn_queue.size() > 0:
            queue_item = conn_queue.pop()[1]  # (origin node, connectionkey, dest_node)
            startpoint = queue_item[0]
            current_conn = queue_item[1]
            endpoint = queue_item[2]
            print(queue_item)

            # visit unvisited nodes, or revisit ones under a new route
            if endpoint not in node_to_dist.keys() or (node_to_dist[endpoint] > node_to_dist[startpoint] + 1):
                node_to_dist[endpoint] = node_to_dist[startpoint] + 1
                node_to_parent[endpoint] = (startpoint, current_conn)

                # add all connections for new or revisited node to the priority queue
                for conn in node_to_connections[endpoint]:
                    new_endpoint = Supergraph.connectionlist[conn].getEndPoint(endpoint)
                    if new_endpoint is not None:
                        conn_queue.insert(node=(endpoint, conn, new_endpoint), priority=1)

        return node_to_dist

    @staticmethod
    def pruneConnections(nodes = list(), connections = list()):
        filtered_connections = set()  # set of filtered connection keys
        # add all connections that point somewhere in the subgraph, filtering the ones pointing out of it
        for conn in connections:
            if Supergraph.connectionlist[conn].getLeftKey() in nodes and Supergraph.connectionlist[conn].getRightKey() in nodes:
                filtered_connections.add(conn)
        return filtered_connections

    @staticmethod
    def getPath(start_node, end_node, nodes = list(), connections = list(), weight_key = "", default_weight = 1):
        # returns tuple of path from start to end in given subgraph as (nodes, connections, path length)
        # returns None if no path exists

        # will pull data from supergraph. If no keys exist default weight is given
        assert default_weight > 0, ValueError

        from PriorityQueue import PriorityQueue

        if start_node not in nodes or end_node not in nodes:    # if either start or end node not in given subgraph
            return None

        if start_node == end_node:
            return ([start_node],list(),0) # return a subgraph of 1 node and 0 connections, with length 0

        filtered_connections = set()       # set of filtered connection keys
        node_to_parent = dict()  # maintains parent heirarchy in BFS as node_to_parent[node] = (origin node, connectionkey)
        node_to_dist = dict()               # maintains distance of given node from start

        node_to_connections = dict()    # maintains dict of node key to sets of connection pointers
        conn_queue = PriorityQueue()    # stores priority queue of weighted connections as tuples of (origin node, connection, dest_node)

        filtered_connections = PathFinder.pruneConnections(nodes, connections)

        # get the dictionary of nodes to sets of connection keys
        for node in nodes:
            node_to_connections[node] = Supergraph.nodeconnectionlist[node].intersection(filtered_connections)

        # add all the connections from the starting node to the queue
        for conn in node_to_connections[start_node]:
            endpoint = Supergraph.connectionlist[conn].getEndPoint(start_node)
            if endpoint is not None:
                conn_queue.insert(node = (start_node,conn,endpoint), priority = 1)

        # initialize start node
        node_to_dist[start_node] = 0
        node_to_parent[start_node] = None

        while conn_queue.size() > 0:
            queue_item = conn_queue.pop()[1]  # (origin node, connectionkey, dest_node)
            startpoint = queue_item[0]
            current_conn = queue_item[1]
            endpoint = queue_item[2]
            # pull weight from connection; use default weight if not acceptable
            weight = Connection.getConnectionData(Supergraph.connectionlist[current_conn],weight_key)
            if (weight == None) or (weight < default_weight):
                weight = default_weight

            # visit unvisited nodes, or revisit ones under a new route
            if endpoint not in node_to_dist.keys() or (node_to_dist[endpoint] > node_to_dist[startpoint] + weight):
                node_to_dist[endpoint] = node_to_dist[startpoint] + weight
                node_to_parent[endpoint] = (startpoint, current_conn)

                # end goal found.
                if endpoint is end_node:
                    parent = node_to_parent[endpoint]
                    returned_nodes = list() # list of nodes in returned path
                    returned_connections = list()   # list of connections in returned path
                    returned_nodes.append(endpoint) # add end node to list
                    # Traverse up parent tree to find path from end back to start
                    while parent is not None:
                        returned_nodes.append(parent[0])
                        returned_connections.append(parent[1])
                        parent = node_to_parent[parent[0]]

                    return (returned_nodes,returned_connections, node_to_dist[endpoint])

                # add all connections for new or revisited node to the priority queue
                for conn in node_to_connections[endpoint]:
                    new_endpoint = Supergraph.connectionlist[conn].getEndPoint(endpoint)
                    if new_endpoint is not None:
                        conn_queue.insert(node=(endpoint, conn, new_endpoint), priority=node_to_dist[endpoint]+weight)

        return None # all connections traversed; no path found

class ArtPointsFinder:
    # Todo: Implement ArtPointsFinder
    pass

    # @staticmethod
    # def getArtPoints(nodes = [], connections = []):
    #     assert type(nodes) is list
    #     assert type(connections) is list
    #     assert len(nodes) > 0
    #     assert len(connections()) > 0
    #
    #     print("Current nodes: ",nodes)
    #     # Returns articulated points, given a list of node and connection keys
    #     node_to_parent = {}             # maintains parent heirarchy in DFS
    #     node_to_time = {}              # maintains discovery time of given node
    #     node_to_low = {}                # maintains low value of given node
    #     counter = 1
    #
    #     node_stack = list(nodes)
    #     current_node_key = ""
    #
    #     unvisited_nodes = list(nodes)
    #     filtered_connections = dict()  # set of filtered connection keys
    #
    #     # add all connections that point somewhere in the subgraph, filtering the ones pointing out of it
    #     for conn in connections:
    #         if Supergraph.connectionlist[conn].getLeftKey() in nodes and Supergraph.connectionlist[conn].getRightKey() in nodes:
    #             filtered_connections.add(conn)
    #
    #     node_to_connections = dict()  # maintains dict of node key to sets of connection pointers
    #     # get the dictionary of nodes to sets of connection keys
    #     for node in nodes:
    #         node_to_connections[node] = Supergraph.nodeconnectionlist[node].intersection(filtered_connections)
    #
    #     while len(node_stack) > 0:
    #         # pop item from stack to create a DFS
    #         current_node_key = node_stack.pop(0)
    #         print("Current node: ", current_node_key)
    #
    #         if current_node_key in unvisited_nodes:
    #             # new node found. Assign values
    #             unvisited_nodes.remove(current_node_key)                # node has now been visited
    #             node_to_time[current_node_key] = counter                # its index is current counter
    #             node_to_parent[current_node_key] = ""                   # its parent is the last enountered node
    #
    #             node_to_low[current_node_key] = counter
    #             counter += 1  # increment counter
    #
    #         # iterate through all connections for the current node
    #         for conn in filtered_connections:
    #             rightkey = Supergraph.connectionlist[conn].getEndPoint(current_node_key)
    #
    #             # from left to right
    #             if leftkey == current_node_key:
    #                 print("Current connection: ", conn, "left:", leftkey, "right: ", rightkey)
    #                 filtered_connections.remove(conn)
    #
    #                 if rightkey in unvisited_nodes:
    #                     print("unvisited",unvisited_nodes)
    #                     # new node found. Assign values
    #                     node_stack.insert(0,rightkey)
    #                     unvisited_nodes.remove(rightkey)  # node has now been visited
    #                     node_to_time[rightkey] = counter  # its index is current counter
    #                     node_to_parent[rightkey] = leftkey  # its parent is the last enountered node
    #                     node_to_low[rightkey] = counter
    #                     counter += 1  # increment counter
    #                     print("Current counter: ", counter)
    #                 elif node_to_low[leftkey] > node_to_low[rightkey]:
    #                     print("\tWAT",leftkey,rightkey)
    #                     temp_value = node_to_time[rightkey]
    #                     child_key = leftkey
    #                     node_to_low[leftkey] = temp_value
    #                     while child_key != "":
    #                         print ("\t" + child_key)
    #                         if node_to_parent[child_key] != "":
    #                             if node_to_low[node_to_parent[child_key]] > node_to_low[child_key]:
    #                                 node_to_low[child_key] = temp_value
    #                         child_key = node_to_parent[child_key]
    #
    #     # at the end print all nodes and data about them
    #     for nodekey in node_to_parent.keys():
    #         print(nodekey, "parent:",node_to_parent[nodekey])
    #         print("index:",node_to_index[nodekey])
    #         print("low:",node_to_low[nodekey])
    #
    #     for conn in connections.keys():
    #         leftkey = connections[conn].leftkey
    #         rightkey = connections[conn].rightkey
    #         if node_to_low[rightkey] < node_to_index[leftkey]:
    #             print(leftkey + " is art point")

class Interpreter:
    S = Supergraph()
    function_names = ['PRINT','PRINTKEYS', 'GETTIME',
                      'SUM', 'SUBTRACT','MULTIPLY', 'DIVIDE',
                      'ABS', 'SQRT', 'SIZE',
                      'NOT', 'AND', 'OR', 'XOR', 'XNOR',
                      'EQ', 'GTEQ', 'LTEQ', 'NEQ', 'LT', 'GT',
                      'SORT',
                      'LOGBASE',
                      'ISNUMERIC', 'HAMMING', 'LEVEN', 'MIN',
                      'MAX', 'SMALLEST', 'LARGEST', 'CHOOSE',
                      'AVG',
                      'RANDOM', 'RANDOMINT',
                      'STRREPLACE',
                      'ADDDATA', 'REMOVEDATA',
                      'LISTNODES', 'ADDNODES', 'GETNODES', 'REMOVENODES',
                      'ADDNODEDATA', 'GETNODEDATA', 'REMOVENODEDATA',
                      'LISTCONNECTIONS','ADDCONNECTIONS','GETCONNECTIONS','REMOVECONNECTIONS',
                      'ADDCONNECTIONDATA', 'GETCONNECTIONDATA', 'REMOVECONNECTIONDATA',
                      'LISTGRAPHS', 'ADDGRAPHS', 'GETGRAPHS', 'REMOVEGRAPHS',
                      'QUERY']
    operators = ['<-->','-->','-', '+', '/', '*', '%', '==', '!=', '>', '<', '>=', '<=', '||', '&&']
    reserved_chars = ['(', ')', '#', '"', "'", '\\', '\t', ',']   # these characters cannot be used in an object name


    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def levenshtein(s1, s2):
        # returns levenshtein distance of two strings
        # code from https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
        if len(s1) < len(s2):
            return Interpreter.levenshtein(s2, s1)

        # len(s1) >= len(s2)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[
                                 j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1  # than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def checkParenCount(expression):
        if expression.count('(') == expression.count(')'):
            return True
        return False

    @staticmethod
    def checkParenStacks(expression):
        # runs through the expression and checks if parentheses are paired up properly
        parencount = 0
        for char in expression:
            if char == '(':
                parencount += 1
            if char == ')':
                parencount -= 1
                if parencount < 0:
                    return False
        return True

    @staticmethod
    def loadKeywords():
        file = open('keywords.txt', 'r')
        keywords = file.readlines()
        for keyword in keywords:
            Interpreter.function_names.append(keyword.rstrip())
        return False

    @staticmethod
    def categorizeToken(token):
        quote_chars = ["'", '"']
        bools = ['true','false']
        null = ["null"]

        if token == '(':
            return '('
        elif token == ')':
            return ')'
        elif token == ',':
            return ','
        elif token in Interpreter.function_names:
            return 'Fun'
        elif token in Interpreter.operators:
            return 'Op'
        elif token.lower() in null:
            return 'V'
        elif token.lower() in bools:
            return 'Boolean'
        elif (len(token) >= 2) and ((token[0] in quote_chars) and (token[len(token) - 1] in quote_chars)):
            return 'Str'
        elif Interpreter.is_number(token):
            return 'Num'
        elif token == '\t':
            return 'Tab'
        elif token == ', ':
            return 'Comma'
        elif token == 'ALL':
            return '*'
        else:
            return '?'     # unknown likely variable

    @staticmethod
    def checkAllTypes(parameters=[], validparamtypes=[]):
        # checks to see if all values in paramtypes match up with valid types
        for param in parameters:
            if type(param) not in validparamtypes:
                return False
        return True

    @staticmethod
    def evaluateFunction(function, parameters):
        # Performs a designated function with the given parameters

        if function == "PRINT":
            # Basic print; will unpack values if only 1 is given
            if len(parameters) == 1:
                print(parameters[0])
            else:
                print(parameters)
            return None

        if function == "PRINTKEYS":
            # Prints all existing keys in the supergraph
            print(Supergraph.getKeyList())
            return None

        if function == "GETTIME":
            # Gets the time in milliseconds from 1970
            if len(parameters) == 0:
                return time.time()
            else:
                raise Exception("Unexpected parameters given")


        if function in ["+", "SUM"]:
            # General sumation function.
            # if given 1 list will sum all items in that list
            # multiple lists will merge the lists into one
            # will concatenate Strings and add numbers
            if len(parameters) == 1 and isinstance(parameters[0],list):
                # add all the items in a single list together
                params = parameters[0]
                return Interpreter.evaluateFunction("SUM", params)
            if Interpreter.checkAllTypes(parameters, [list]):
                # merge multiple lists together
                returnlist = []
                for param in parameters:
                    returnlist.extend(param)
                return returnlist
            elif Interpreter.checkAllTypes(parameters, [int, float]):
                # Add numbers
                result = 0
                if len(parameters) >= 1:
                    for param in parameters:
                        result += param
                return result
            elif Interpreter.checkAllTypes(parameters, [int, float, str]):
                # A mix will produce a string
                result = ""
                if len(parameters) >= 1:
                    for param in parameters:
                        result += str(param)
                return result
            else:
                raise Exception("Unexpected parameters given")

        if function in ["-", "SUBTRACT"]:
            if len(parameters) == 2:
                if Interpreter.checkAllTypes(parameters, [int, float]):
                    return float(parameters[0]) - float(parameters[1])
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 Parameters expected")

        if function in ["*", "MULTIPLY"]:
            if len(parameters) == 2:
                if Interpreter.checkAllTypes(parameters, [int, float]):
                    return ["Num", float(parameters[0]) * float(parameters[1])]
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 Parameters expected")

        if function in ["/", "DIVIDE"]:
            if len(parameters) == 2:
                if Interpreter.checkAllTypes(parameters, [int, float]):
                    return float(parameters[0]) / float(parameters[1])
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 Parameters expected")

        if function in ["%", "MOD"]:
            if len(parameters) == 2:
                if Interpreter.checkAllTypes(parameters, [int, float]):
                    return float(parameters[0]) % float(parameters[1])
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 Parameters expected")

        if function in ["ABS"]:
            if len(parameters) == 1:
                if Interpreter.checkAllTypes(parameters, [int, float]):
                    return abs(float(parameters[0]))
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("1 Parameter expected")

        if function in ["SQRT"]:
            if len(parameters) == 1:
                if Interpreter.checkAllTypes(parameters, [int, float]):
                    result = parameters[0] ** (1.0 / 2) #raise the power of parameter to 1/2, giving square root
                    return result
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("1 Parameter expected")

        if function == "SIZE":
            if len(parameters) == 1:
                if isinstance(parameters[0],(list,str)):
                    return len(parameters[0])
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("Too many parameters given")

        if function == "NOT":
            if len(parameters) == 1:
                if type(parameters[0]) is bool:
                    return (not parameters[0])
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("Too many parameters given")

        if function in ["&&","AND"]:
            if len(parameters) >= 2:
                if Interpreter.checkAllTypes(parameters, [bool]):
                    for param in parameters:
                        if not param:
                            return False
                    return True
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 or more parameters expected")

        if function in ["||","OR"]:
            if len(parameters) >= 2:
                if Interpreter.checkAllTypes(parameters, [bool]):
                    for param in parameters:
                        if param:
                            return True
                    return False
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 or more parameters expected")

        if function == "XOR":
            if len(parameters) >= 2:
                if Interpreter.checkAllTypes(paramtypes, ['Boolean']):
                    truecount = 0
                    for param in parameters:
                        if param.lower() == 'true':
                            truecount += 1
                    if (truecount % 2) == 1:
                        return ["Boolean", 'true']
                    return ["Boolean", 'false']
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 or more parameters expected")

        if function == "XNOR":
            if len(parameters) >= 2:
                if Interpreter.checkAllTypes(paramtypes, ['Boolean']):
                    truecount = 0
                    for param in parameters:
                        if param.lower() == 'true':
                            truecount += 1
                    if (truecount % 2) == 0:
                        return ["Boolean", 'true']
                    return ["Boolean", 'false']
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 or more parameters expected")

        if function in ["==","EQ"]:
            # Equals function
            if len(parameters) >= 2:
                if not Interpreter.checkAllTypes(parameters, [list]):
                    for index in range(1,len(parameters)):
                        if parameters[index] != parameters[0]:
                            return False
                    return True
                else:
                    raise Exception("Cannot compare lists")
            else:
                raise Exception("2 or more parameters expected")

        if function in ["!=","NEQ"]:
            # Not Equals function. All items must by unique values to return true
            if len(parameters) >= 2:
                if not Interpreter.checkAllTypes(parameters, [list]):
                    itemset = []    #set of all unique items
                    for param in parameters:
                        if param in itemset:
                            return False
                        itemset.append(param)
                    return True
                else:
                    raise Exception("Cannot compare lists")
            else:
                raise Exception("2 or more parameters expected")

        if function in [">=","GTEQ"]:
            # Greater than. Will return false if items are not sorted in descending order
            if len(parameters) >= 2:
                if Interpreter.checkAllTypes(paramtypes, ['Num']):
                    for index in range(1,len(parameters)):
                        if parameters[index-1] <= parameters[index]:
                            return ["Boolean", 'false']
                    return ["Boolean", 'true']
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 or more parameters expected")

        if function in ["<=","LTEQ"]:
            # Greater than. Will return false if items are not sorted in descending order
            if len(parameters) >= 2:
                if Interpreter.checkAllTypes(paramtypes, ['Num']):
                    for index in range(1,len(parameters)):
                        if parameters[index-1] >= parameters[index]:
                            return ["Boolean", 'false']
                    return ["Boolean", 'true']
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 or more parameters expected")

        if function in [">","GT"]:
            # Greater than. Will return false if items are not sorted in descending order
            if len(parameters) >= 2:
                if Interpreter.checkAllTypes(paramtypes, ['Num']):
                    for index in range(1,len(parameters)):
                        if parameters[index-1] < parameters[index]:
                            return ["Boolean", 'false']
                    return ["Boolean", 'true']
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 or more parameters expected")

        if function in ["<","LT"]:
            # Greater than. Will return false if items are not sorted in descending order
            if len(parameters) >= 2:
                if Interpreter.checkAllTypes(parameters, [int, float]):
                    for index in range(1,len(parameters)):
                        if parameters[index-1] > parameters[index]:
                            return False
                    return True
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 or more parameters expected")

        if function in ["SORT"]:
            # Returns a sorted list
            if Interpreter.checkAllTypes(parameters, [str, int, float]):
                numlist = []
                strlist = []
                for index in range(0,len(parameters)):
                    if parameters[index] is str:
                        strlist.append(parameters[index])
                    else:
                        numlist.append(parameters[index])

                numlist.sort()
                strlist.sort()
                sortedlist = numlist+strlist
                print("sorted list: ", sortedlist)
                return sortedlist
            else:
                raise Exception("Unexpected parameters given")

        if function in ["LEVEN"]:
            if len(parameters) == 2:
                if Interpreter.checkAllTypes(parameters, [str]):
                    return Interpreter.levenshtein(parameters[0], parameters[1])
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("2 Parameters Expected")

        if function in ["AVG"]:
            if Interpreter.checkAllTypes(parameters, [int, float]):
                if len(parameters) > 0:
                    sum = 0
                    result = 0
                    for param in parameters:
                        sum += float(param)
                    result = sum / len(parameters)
                    return result
                else:
                    raise Exception("At least one parameter must be supplied")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["RANDOM"]:
            # Returns random float between 0 and x, or in range if two numbers given
            if Interpreter.checkAllTypes(parameters, [int, float]):
                if len(parameters) == 2:
                        return random.uniform(parameters[0],parameters[1])
                if len(parameters) == 1:
                        return random.uniform(0,parameters[0])
                raise Exception("1 or 2 numbers expected")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["RANDOMINT"]:
            # Returns random int between 0 and x, or in range if two numbers given
            if Interpreter.checkAllTypes(parameters, [int, float]):
                if len(parameters) == 2:
                    return int(random.uniform(parameters[0], parameters[1]))
                if len(parameters) == 1:
                    return int(random.uniform(0, parameters[0]))
                raise Exception("1 or 2 numbers expected")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["ADDDATA"]:
            if len(parameters) == 2:
                #  varname,  vardata
                if isinstance(parameters[0],str):
                    # print Supergraph.verifyNodeNames(parameters[0])
                    Supergraph.addData(parameters[0], parameters[1])
                    return None
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["REMOVEDATA"]:
            if len(parameters) == 1:
                #  varname,  vardata
                if isinstance(parameters[0],str):
                    # print Supergraph.verifyNodeNames(parameters[0])
                    Supergraph.removeData(parameters[0])
                    return None
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["LISTNODES"]:
            if len(parameters) > 0:
                raise Exception("Unexpected parameters given")
            Supergraph.printNodeList()
            return None

        if function in ["ADDNODES"]:
            if not Interpreter.checkAllTypes(parameters, [str]):
                raise Exception("Only strings can be added as node keys")
            for param in parameters:
                Supergraph.addNode(param)
            return Supergraph.verifyNodeNames(parameters)

        if function in ["GETNODES"]:
            # converts a list of names into a nodelist,  removing ones that don't exist in the supergraph
            if len(parameters) > 1:
                if Interpreter.checkAllTypes(parameters, [str]):
                    nodekeys = Supergraph.verifyNodeNames(parameters)
                    return nodekeys
                raise Exception("Unexpected parameters given")
            else:
                nodekeys = Supergraph.getAllNodeKeys()
                return nodekeys

        if function == "REMOVENODES":
            if len(parameters) > 1:
                if Interpreter.checkAllTypes(parameters, [str]):
                    Supergraph.removeNodes(Supergraph.verifyNodeNames(parameters))
                    return None
                raise Exception("Unexpected parameters given")
            elif len(parameters) == 1:
                if isinstance(parameters[0],str):
                    Supergraph.removeNodes(Supergraph.verifyNodeNames(parameters))
                    return None
                elif isinstance(parameters[0],list):
                        Supergraph.removeNodes(Supergraph.verifyNodeNames(parameters[0]))
                        return None
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["ADDNODEDATA"]:
            if len(parameters) == 3:
                # nodenames(L),  varname,  vardata
                if isinstance(parameters[0],list) and isinstance(parameters[1],str):
                    if Interpreter.checkAllTypes(parameters[0], [str]):
                        Supergraph.addNodeData(parameters[0], parameters[1], parameters[2])
                        return None
                    else:
                        raise Exception("Unexpected parameters given")
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["REMOVENODEDATA"]:
            if len(parameters) == 3:
                # nodenames,  varname
                if isinstance(parameters[0], list) and isinstance(parameters[1],str):
                    # print Supergraph.verifyNodeNames(parameters[0])
                    if Interpreter.checkAllTypes(parameters[0], [str]):
                        Supergraph.removeNodeData(parameters[0], parameters[1])
                        return None
                raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["GETNODEDATA"]:
            if len(parameters) == 2:
                # nodenames,  varname
                if isinstance(parameters[0], list) and isinstance(parameters[1], str):
                    if Interpreter.checkAllTypes(parameters[0], [str]):
                        returnlist = Supergraph.getNodeData(parameters[0], parameters[1])
                        return returnlist
                raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["LISTCONNECTIONS"]:
            if len(parameters) > 0:
                raise Exception("Unexpected parameters given")
            Supergraph.printConnectionList()
            return None

        if function in ['-->','<-->',"ADDCONNECTIONS"]:
            if len(parameters) in [2,3]:
                # ADDCONNECTIONS(leftnodes, rightnodes)
                # Get initial left and right keys
                # They're treated as lists even if they might be one item
                leftkeys = [parameters[0]]
                rightkeys = [parameters[1]]

                # if list type detected, unpack the list
                if isinstance(parameters[0],list):
                    leftkeys = parameters[0]
                if isinstance(parameters[1],list):
                    rightkeys = parameters[1]

                # get the direction of the connections
                con_direction = "both"
                if function == '-->':
                    con_direction = "right"
                if len(parameters) == 3:
                    con_direction = parameters[2]

                Supergraph.addConnections(leftkeys, rightkeys,con_direction)
                return None
            else:
                raise Exception("Unexpected parameters given")

            
        if function in ["GETCONNECTIONS"]:
            # converts a list of names into a connectionlist,  removing ones that don't exist in the supergraph
            if len(parameters) > 1:
                if Interpreter.checkAllTypes(parameters, [str]):
                    connectionkeys = Supergraph.verifyConnectionNames(parameters)
                    return connectionkeys
                raise Exception("Unexpected parameters given")
            else:
                connectionkeys = Supergraph.getAllConnectionKeys()
                return connectionkeys

        if function in ["REMOVECONNECTIONS"]:
            if len(parameters) == 1 and isinstance(parameters[0],list):
                if Interpreter.checkAllTypes(parameters[0], [str]):
                    Supergraph.removeConnections(Supergraph.verifyConnectionNames( parameters[0]))
                    return None
                raise Exception("Unexpected parameters given")
            elif len(parameters) >= 1:
                if Interpreter.checkAllTypes(parameters, [str]):
                    Supergraph.removeConnections(Supergraph.verifyConnectionNames( parameters))
                    return None
                raise Exception("Unexpected parameters given")
            elif len(parameters) == 0:
                Supergraph.removeConnections(Supergraph.getAllConnectionKeys())
                return None
            else:
                raise Exception("Unexpected parameters given")

        if function in ["ADDCONNECTIONDATA"]:
            if len(parameters) == 3:
                # connectionnames(L),  varname,  vardata
                if isinstance(parameters[0],list) and isinstance(parameters[1],str):
                    if Interpreter.checkAllTypes(parameters[0], [str]):
                        Supergraph.addConnectionData(parameters[0], parameters[1], parameters[2])
                        return None
                    else:
                        raise Exception("Unexpected parameters given")
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["REMOVECONNECTIONDATA"]:
            if len(parameters) == 2:
                # connectionnames,  varname
                if isinstance(parameters[0],list) and isinstance(parameters[1],str):
                    if Interpreter.checkAllTypes(parameters[0], [str]):
                        Supergraph.removeConnectionData(parameters[0], parameters[1])
                        return None
                raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["GETCONNECTIONDATA"]:
            if len(parameters) == 2:
                # connectionnames,  varname
                if isinstance(parameters[0], list) and isinstance(parameters[1], str):
                    if Interpreter.checkAllTypes(parameters[0], [str]):
                        return Supergraph.getConnectionData(parameters[0], parameters[1])
                raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        if function in ["LISTGRAPHS"]:
            if len(parameters) > 0:
                raise Exception("Unexpected parameters given")
            Supergraph.printGraphList()
            return None

        if function in ["ADDGRAPHS"]:
            if Interpreter.checkAllTypes(parameters, [str]):
                for param in parameters:
                    Supergraph.addGraph(param)
            else:
                raise Exception("Unexpected parameters given")
            return None
        
        if function in ["GETGRAPHS"]:
            # converts a list of names into a graphlist,  removing ones that don't exist in the supergraph
            if len(parameters) > 1:
                if Interpreter.checkAllTypes(parameters, [str]):
                    return Supergraph.verifyGraphNames(parameters)
                else:
                    raise Exception("Unexpected parameters given")
            else:
                return Supergraph.getAllGraphKeys()
        
        if function in ["REMOVEGRAPHS"]:
            if len(parameters) >= 1:
                if Interpreter.checkAllTypes(parameters, [str]):
                    Supergraph.removeGraphs(Supergraph.verifyGraphNames(parameters))
                    return None
                else:
                    raise Exception("Unexpected parameters given")
            else:
                Supergraph.removeGraphs(Supergraph.getAllGraphKeys())
                return None

        if function in ["QUERY"]:
            # Run a query on a selected group of objects, only giving the ones where the expression returns true
            # Keyword THIS is used for this function to refer to object being currently queried
            if len(parameters) == 2:
                # object list(L), query expression(Str)
                if isinstance(parameters[0], list) and isinstance(parameters[1], str):
                    if Interpreter.checkAllTypes(parameters[0], [str]):
                        returnlist = [] # Maintains list of keys that satisfied query
                        # iterate through items in key list
                        for queryitem in parameters[0]:
                            result = Interpreter.evaluateExpression(parameters[1], queryitem)
                            if result == [[True]]:
                                returnlist.append(queryitem)
                        return returnlist
                else:
                    raise Exception("Unexpected parameters given")
            else:
                raise Exception("Unexpected parameters given")

        # return error if no function defintion found
        raise Exception("Unknown function " + function)

    @staticmethod
    def evaluateExpression(expression, this = ""):
        # Evaluates an expression. Tokenizes it, then evaluates the tokens
        # this variables references what the keyword THIS references in the supergraph
        print("EXPRESSION: "+expression)
        tokenlist = Interpreter.tokenizeExpression(expression)
        #print tokenlist
        return Interpreter.evaluateTokens(tokenlist, this)

    @staticmethod
    def evaluateTokens(tokenlist, this = ""):
        # parameter stacks
        paramStack = [[]]  # holds parameter lists
        paramHeights = [0] # Maintains the parenthesis depth of each list in paramStack
        # operation/function stacks
        opStack = []       # Actual operation/function name
        opHeight = []      # Parenthesis depth of function/operator
        opType = []        # Determines whether an operator or a function
        # height
        current_height = 0 # Used for keeping track of the current parenthesis depth

        data_pointer = "."  # Used for pointers that pull data from supergraph. NAME.DATA

        previous_category = None

        # tokenize the input expression

        # run through each token and evaluate expression
        for token in tokenlist:
            # get the category of the current token to determine what to do
            category = Interpreter.categorizeToken(token)
            # print category

            if category == '(':
                # increase the height
                current_height += 1
                # make a new parameter list at new height
                paramStack.append([])
                paramHeights.append(current_height)
            elif category == ',':
                # To prevent crosstalk between parameters in a function, new parameters are thrown onto the stack
                # vertically rather than horizontally
                # The height is kept the same, and when a function is being evaluated at ) they are compressed into one
                # before evaluation
                paramStack.append([])
                paramHeights.append(current_height)
            elif category == ')':

                #compress the parameters seperated by commas into one list
                while len(paramStack) > 1 and paramHeights[-2] == paramHeights[-1]:
                    paramStack[-2] = paramStack[-2] + paramStack[-1]
                    paramStack.pop()
                    paramHeights.pop()


                # set height to one less,  and update height of topmost parameters
                current_height -= 1
                paramHeights[-1] = current_height

                #  check for possible function call
                if (len(opStack) > 0) and opType[-1] == 'Fun':
                    # check if function and current parameter heights match up
                    if opHeight[-1] == paramHeights[-1]:
                        # Evaluate result of function call
                        result = Interpreter.evaluateFunction(opStack[-1], paramStack[-1])
                        #print("result: ", result)

                        # Add results to stacks
                        paramStack[-1] = [result]

                        # pop function from stack
                        opType.pop()
                        opHeight.pop()
                        opStack.pop()

                # merge the paramaters list within the parenthesis with ones "below" them
                # EX: 3, (4, 5) <-> [[3], [4, 5]] becomes  3, 4, 5 <-> [[3, 4, 5]]
                paramStack[-2] = paramStack[-2] + paramStack[-1]
                paramStack.pop()
                paramHeights.pop()

            elif category == "Fun" or category == "Op":
                # Add operation/function to operation stack
                opStack.append(token)
                opType.append(category)
                opHeight.append(current_height)

                # If two operations are at the same height there's a problem
                if len(opHeight) > 1:
                    if opHeight[-1] == opHeight[-2]:
                        if opType[-1] == opType[-2]:
                            raise Exception("Unsuccessful evaluation of operation "+opStack[-2])

            elif category == "Str":
                # Add new parameter to the list at the top of the stack
                paramStack[-1].append(token[1:-1]) # remove the " from start and end of string
            elif category == "Num":
                # Add new numeric parameter to the list at the top of the stack
                paramStack[-1].append(float(token))
            elif category in ["Boolean"]:
                # Add new boolean parameter to the list at the top of the stack
                paramStack[-1].append(token.lower() in ['true'])
            elif category in ["V"]:
                # Add new parameter to the list at the top of the stack
                paramStack[-1].append(None)
            elif category == "?":
                # Unknown category; search supergraph for data and inject it if possible
                data = Supergraph.getData(token)
                if data is not None:
                    paramStack[-1].append(data)
                else:
                    # Failed to find anything in supergraph; look in objects in supergraph
                    pointers = token.split(data_pointer)
                    data = Supergraph.getPointerData(pointers, this)
                    if data is not None:
                        paramStack[-1].append(data)
                    else:
                        paramStack[-1].append(None)
                        #raise Exception("Unable to find value of "+token)

            # At end,  check if a binary operation is possible.
            # Don't process operations immediately when encountered to prevent accidental postfix processing
            if len(opStack) > 0 and category not in ["Op","Fun"]:
                if opType[-1] == 'Op':
                    # check if 2 or more parameters in topmost list
                    if len(paramStack[-1]) > 1:
                        # check if height of top list and top operator match
                        if opHeight[-1] == paramHeights[-1]:
                            # get left and right values
                            rightparam = paramStack[-1].pop()
                            leftparam = paramStack[-1].pop()
                            # Evaluate the binary operator
                            result = Interpreter.evaluateFunction(opStack[-1], [leftparam, rightparam])
                            #print("result: ", result)

                            # put results in stacks
                            paramStack[-1].append(result)
                            # remove operator from top of stack
                            opType.pop()
                            opHeight.pop()
                            opStack.pop()
                    # Negating numbers. Check if only 1 number on stack,  and topmost operator is -
                    elif len(paramStack[-1]) == 1 and opStack[-1] == "-":
                        # check if height of top list and top operator match,  and current token is not operator
                        if (opHeight[-1] == paramHeights[-1]) and category != "Op":
                            # get topmost parameter
                            rightparam = paramStack[-1].pop()
                            # Negate the value
                            result = Interpreter.evaluateFunction(opStack[-1], [0, rightparam])

                            # put results in stacks
                            paramStack[-1].append(result)
                            # remove operator from top of stack
                            opType.pop()
                            opHeight.pop()
                            opStack.pop()
            previous_category = category

        #print 'END OF EVALUATION PARAMETERS: ',paramStack

        if len(paramStack) == 1:
            return paramStack

    @staticmethod
    def tokenizeExpression(expression):
        # Improved algorithm for tokenizing a math expression

        is_quoted = False
        is_escaped = False
        quote_chars = ["'", '"']
        outer_quote_char = None  # will be ' or " once a quote starts
        comment_substring = '#'
        tab = '\t'

        regstring = '(<-->|-->|\*|/|\+|\-|\(|\)|%|==|!=|>=|<=|>|<|&&|\\|\\||in|,|"|\'|#|\\\\'+"|"+tab+"|"+comment_substring + ")"
        initial_tokens = re.split(regstring, expression)    # tokenize the expression initially
        final_tokens = []   # final token list

        # print initial_tokens

        for token in initial_tokens:
            if not is_quoted:
                # not being parsed as a string
                if token == comment_substring:
                    # start of a comment; stop tokenizing
                    break
                elif token in quote_chars:
                    # start of a string
                    final_tokens.append(token)
                    is_quoted = True
                    outer_quote_char = token
                else:
                    # a normal token like an operator, parenthesis, function, or variable
                    cleantoken = token.replace(' ','')
                    if len(cleantoken) > 0:  #  strip whitespace from current token
                        final_tokens.append(cleantoken)
            else:
                # is quoted
                if token == "\\":
                    # at escape char
                    if is_escaped:
                        # add escape char as literal
                        final_tokens[-1] = final_tokens[-1] + "\\"
                        is_escaped = False
                    else:
                        # first escape character
                        is_escaped = True
                elif token == outer_quote_char:
                    # at quote char
                    if not is_escaped:
                        # Quote is not escaped; end quote mode
                        is_quoted = False
                    final_tokens[-1] = final_tokens[-1] + token
                    is_escaped = False
                else:
                    if len(token) > 0:
                        # merge any tokens into a single string token
                        # this is the body of the string
                        final_tokens[-1] = final_tokens[-1] + token
                        is_escaped = False

        return final_tokens

    @staticmethod
    def checkTokenLegality(token):
        # returns True if token is not a keyword used by database
        assert type(token) is str
        if token in Interpreter.function_names:
            return False
        if token in Interpreter.operators:
            return False
        for illegal_char in Interpreter.reserved_chars:
            if illegal_char in token:
                return False
        return True

class FileHandler:

    @staticmethod
    def writeGraphFileJSON(filename="", version_num=1.00,
                       nodekeys=[], connectionkeys=[], graphkeys=[]):

        json_dict = {}
        json_dict["Nodes"] = {}
        json_dict["Connections"] = {}
        json_dict["Graphs"] = {}

        nodes = Supergraph.namesToNodes(nodekeys)

        for node in nodes:
            json_dict["Nodes"][node.name] = node.nodedata

        connections = Supergraph.namesToConnections(connectionkeys)

        for conn in connections:
            json_dict["Connections"][conn.name] = conn.connectiondata

        graphs = Supergraph.namesToGraphs(graphkeys)

        for graph in graphs:
            json_dict["Graphs"][graph.name]["nodekeys"] = graph.nodekeys
            json_dict["Graphs"][graph.name]["connectionkeys"] = graph.connectionkeys

        with open(filename, 'w') as outfile:
            json.dump(json_dict, outfile, indent=4, sort_keys=True)

    @staticmethod
    def readGraphFile(filename=""):
        #TODO Implement reading file
        return

class GraphGenerator:
    def generateCompleteGraph(node_basename,connection_basename, node_count, prevent_recursive = True):
        assert type(node_count) is int, ValueError
        assert node_count >= 1, ValueError

        nodes = Supergraph.addNodes(nodenames = ([node_basename] * node_count),nodedata=dict,add_if_exists=True)
        connections = Supergraph.addConnections(leftnames=nodes,rightnames=nodes,direction="both",generator=connection_basename,prevent_recursive=prevent_recursive)
        return (nodes,connections)

    def generateRingGraph(node_basename, connection_basename, ring_size, direction):
        # generates a ring graph, wrapping generateLineGraph
        return GraphGenerator.generateLineGraph(node_basename, connection_basename, ring_size, direction, True)

    def generateLineGraph(node_basename, connection_basename, line_size, direction, loop_to_start = False):
        # generates a line graph using the given names for key generators
        # size and direction(bidirectional or unidirectional) as specified
        # will loop back forming a ring if desired
        # returns a tuple containing the keys of each

        assert type(line_size) is int, ValueError
        assert line_size >= 1, ValueError
        assert direction in ["right", "both"], ValueError

        returned_nodes = set()
        returned_connections = set()
        first_node = Supergraph.addNode(node_basename, add_if_exists=True)
        last_node = first_node
        left_node = first_node
        returned_nodes.add(left_node)
        for i in range(line_size - 1):
            right_node = Supergraph.addNode(node_basename, add_if_exists=True)
            returned_nodes.add(right_node)
            last_node = right_node
            conn = Supergraph.addConnection(connection_basename, left_node, right_node, direction)
            left_node = right_node
            returned_connections.add(conn)

        # loop back to first node if told to
        if loop_to_start:
            conn = Supergraph.addConnection(connection_basename, last_node, first_node, direction)
            returned_connections.add(conn)

        return (returned_nodes, returned_connections)

import time # used for getting unix time
import queue    # used for priority queues
import re       # regex library
import random   # used for random functions
import json
import GraphRenderer

from time import time, sleep
start_time = time()

Configurations.setRuntimeConfigs()

# file = open(Configurations.config_values["runtime_script"], 'r')
# x = file.readlines()
# for i in x:
#     Interpreter.evaluateExpression(i.rstrip())
#
# print("writing to file")
# FileHandler.writeGraphFileJSON("graphfile.json","1",Supergraph.nodelist.keys(),Supergraph.connectionlist.keys())


# print(Supergraph.getAllNodeKeys())
# #print "connections: ",Supergraph.getAllConnectionKeys()
# Supergraph.addConnections(["NODE1"],["NODE2"],'right')
# print("degrees",Supergraph.getNodeDegrees(nodenames = Supergraph.getAllNodeKeys(), degree = "in"))
# Supergraph.removeNodes(Supergraph.getAllNodeKeys())
# Supergraph.removeConnections(Supergraph.getAllConnectionKeys())
#
# # testing in and out degrees more
nodelist1 = ["N1","N2","N3","N4"]
nodelist2 = ["N6","N7","N8","N9"]
Supergraph.addNodes(nodelist1)
Supergraph.addNodes(nodelist2)
Supergraph.addNode("N5")
Supergraph.addConnections(nodelist1,["N5"],"both")
Supergraph.addConnections(["N5"],nodelist2,"both")
Supergraph.addConnectionData(Supergraph.getAllConnectionKeys(),"testing",5)

# print("degrees",Supergraph.getNodeDegrees(nodenames = Supergraph.getAllNodeKeys(), degree = "in"))
# print("degrees",Supergraph.getNodeDegrees(nodenames = Supergraph.getAllNodeKeys(), degree = "out"))
#
# print("result:",Supergraph.getNodeNeighbors(["N1"]))
# print("result:",Supergraph.getNodeNeighbors(Supergraph.getNodeNeighbors(["N1"])))

# # testing rendering system
# circles_list = ["a","b","c","d","e","f","g"]
# edges = [["a","b"],["a","c"],["c","d"],["e","f"]]
# GraphRenderer.draw_circular_graph(circles_list,edges,"Graph Renders\\circular_test_1.png", 400,400,10,100,(255,255,255),(0,0,0),(0,255,0))
# GraphRenderer.draw_scatter_graph(circles_list,edges,"Graph Renders\\scatter_test_1.png", 400,400,10,0,(255,255,255),(0,0,0),(0,255,0))
# GraphRenderer.draw_scatter_graph(circles_list,edges,"Graph Renders\\scatter_test_2.png", 400,400,10,0,(255,255,255),(255,0,255),(0,255,0))

#ArtPointsFinder.getArtPoints(Supergraph.getAllNodeKeys(),Supergraph.connectionlist)

# testing pathfinding
print("resulting path: ",PathFinder.getPath(start_node="N1",end_node="N9",nodes=Supergraph.getAllNodeKeys(),connections=Supergraph.connectionlist.keys(),weight_key="testing"))

# # testing eigenvector centrality
# Supergraph.removeNodes(Supergraph.getAllNodeKeys())
# Supergraph.removeConnections(Supergraph.getAllConnectionKeys())
# nodelist1 = ["N1","N2","N3","N4","N5"]
# Supergraph.addNodes(nodelist1)
# Supergraph.addConnections(["N1"],["N2","N3","N4"],"right")
# Supergraph.addConnections(["N2"],["N3","N4"],"right")
# Supergraph.addConnections(["N3"],["N1"],"right")
# Supergraph.addConnections(["N4"],["N1","N3"],"right")
# Supergraph.addConnections(["N4"],["N5"],"right")
# print(GraphCentrality.getEigenVectorCentrality(nodes=Supergraph.getAllNodeKeys(),connections=Supergraph.connectionlist.keys()))

# testing pathfinding
Supergraph.removeNodes(Supergraph.getAllNodeKeys())
Supergraph.removeConnections(Supergraph.getAllConnectionKeys())

    # generate a line graph divided into two sections
nodelist1 = []
for i in range(0,2000):
    nodelist1.append("N"+str(i))

Supergraph.addNodes(nodelist1)

# for node in range(int(len(nodelist1)/2) -1):
#     Supergraph.addConnections([nodelist1[node]],[nodelist1[node+1]],"right")

# for node in range(int(len(nodelist1)/2), len(nodelist1)-1):
#     Supergraph.addConnections([nodelist1[node]],[nodelist1[node+1]],"both")

for node in range(len(nodelist1)-1):
    Supergraph.addConnections([nodelist1[node]],[nodelist1[node+1]],"right")
Supergraph.addConnections([nodelist1[len(nodelist1)-1]],[nodelist1[0]],"right")

# PathFinder.getUnweightedAllPairs(nodes=Supergraph.getAllNodeKeys(),connections=Supergraph.connectionlist.keys())

# testing generators
line_graph = GraphGenerator.generateRingGraph(node_basename="node",connection_basename="connection",ring_size=20,direction="both")
print("resulting nodes",line_graph[0])
print("resulting connections",line_graph[1])

end_time = time() - start_time
print("time of execution",end_time)

#                      __
#         _______     /*_)-< HISS HISS
#   ___ /  _____  \__/ /
#  <____ /      \____ /