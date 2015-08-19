#!/usr/bin/env python
"""
Library: neural_net

An object oriented neural network library. Instead of dense matrices
representing connections, neurons (one object) are connected to other neurons
via dendrites (another object). The 'weight' of the connection then is a
property of the connecting dendrite.

This allows for exploration of neural networks with arbitrary organization as
opposed to simple layers.

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import math
import random

import pylib.osscripts as oss
import pylib.xmlparse as xp

class NNException(Exception): pass

#-------------------------------------------------------------------------------
def logisticFunction(x):
#-------------------------------------------------------------------------------
    return 1 / (1 - math.exp(-x))


#-------------------------------------------------------------------------------
def Dx_logisticFunction(x):
#-------------------------------------------------------------------------------
    return x * (1 - x)


#-------------------------------------------------------------------------------
def sigmoid(x):
#-------------------------------------------------------------------------------
    return math.tanh(x)


#-------------------------------------------------------------------------------
def dsigmoid(y):
#-------------------------------------------------------------------------------
    return 1.0 - y**2


#-------------------------------------------------------------------------------
class Dendrite(object):
#-------------------------------------------------------------------------------
    """ dendrites serve as the connecting element between the neural elements
        within the neural network. A dendrite is associated with one neural
        element and connects in a different one.
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, elem=None, weight=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        ## the element being connected via this dendrite to the owning neural
        ## element of this dendrite
        self.elem = elem

        ## weight is the weight of this particular connection
        self.weight = weight if weight is not None else (2 * random.random() - 1.0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def asXmlNode(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return xp.xmlNode('<dendrite elem="%s" weight="%1.20f"/>' % (self.elem.id, self.weight))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xmlLoad(self, xn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.elem = xn['elem']
        self.weight = float(xn['weight'])
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def resolveRefs(self, refs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(self.elem, unicode):
            self.elem = refs[self.elem]


#-------------------------------------------------------------------------------
class NeuralElement(object):
#-------------------------------------------------------------------------------
    """ A base class for the neural elements within the network. These include
        'sensors' and neurons of various types.
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, _=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.id = id(self)
        self.activation = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def train(self, error):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return str(self.__dict__)


#-------------------------------------------------------------------------------
class Sensor(NeuralElement):
#-------------------------------------------------------------------------------
    """ Sensors represent neural elements that unlike neurons have no incoming
        dendrites. In use, the sensors are the input layer of the neural network
        and the values are set by the calling program.
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getActivation(self, ct=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.activation

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def asXmlNode(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return xp.xmlNode('<sensor id="%s"/>' % (self.id))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xmlLoad(self, xn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.id = xn['id']
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def activate(self, v):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.activation = v


#-------------------------------------------------------------------------------
class Neuron(NeuralElement):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, inputs=None, trainingRate=0.5, initialActivation=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        NeuralElement.__init__(self)

        ## connect the inputs to this neuron via dendrites
        self.inputs = [Dendrite(input) for input in inputs] if inputs is not None else []

        self.trainingRate = trainingRate
        self.activation = initialActivation
        self.ctime = -1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addConnection(self, neuron, weight=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ dynamic means of adding connected neurons
        """
        self.inputs.append(Dendrite(neuron, weight))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rmConnection(self, neuron):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ dynamic means of removing connected neurons
        """
        elem = None
        for dendrite in self.inputs:
            if dendrite.elem is neuron:
                elem = dendrite
                break

        if elem is not None:
            self.inputs.remove(elem)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getActivation(self, currentTime=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if currentTime is not None and currentTime != self.ctime:
            ## setting time prevents infinite loop if output feeds into itself
            self.ctime = currentTime
            self.activation = sigmoid(sum([d.elem.getActivation(currentTime) * d.weight for d in self.inputs]))

        return self.activation

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def train(self, error, trainingRate=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ performs back propagation training by taking the 'error' generated
            between the actual output of the neuron versus the desired input and
            driving it back to its input neurons and then adjusting the weight
            of the connection (stored in the dendrite).

            'error' is positive if we need this activation to go up
        """
        if trainingRate is None:
            trainingRate = self.trainingRate

        delta = dsigmoid(self.activation) * error
        #if -0.005 < delta < 0.005: delta = 0.05 if self.activation > 0 else -0.05

        for dendrite in self.inputs:
            dendrite.elem.train(dendrite.weight * delta)
            dendrite.weight += trainingRate * delta * dendrite.elem.getActivation()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def asXmlNode(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xn = xp.xmlNode('<neuron id="%s" trainingRate="%f" activation="%f"/>' % (self.id, self.trainingRate, self.activation))
        for i in self.inputs:
            xn.add(i.asXmlNode())
        return xn

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xmlLoad(self, xn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.id = xn['id']
        self.trainingRate = float(xn['trainingRate'])
        self.activation = float(xn['activation'])
        for xd in xn.nodes:
            self.inputs.append(Dendrite().xmlLoad(xd))
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def resolveRefs(self, refs):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for i in self.inputs:
            i.resolveRefs(refs)


#-------------------------------------------------------------------------------
class BiasNeuron(Neuron):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, val=1.0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Neuron.__init__(self, initialActivation=val)


#-------------------------------------------------------------------------------
class NeuralNetwork(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name=None, inputNum=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.name = name
        self.formatVersion = '1.1'
        self.numHidden = 0
        self.currentTime = 0
        self.sensors = self.allocLayer(inputNum, None, Sensor)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def encode(self, v, mx, mn=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ normalize values 'v' to the range ['mn', 'mx')
        """
        return 2.0 * (v - mn) / (mx - mn) - 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def decode(self, v, mx, mn=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ restore previously normalized values
        """
        return (v + 1) * (mx - mn) / 2.0 + mn

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setInput(self, inVec, mx=1, mn=-1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ take the input vector 'inVec' and place the 'encoded' values into
            the input neurons of the network (sensors) in the terminology used
            here.
        """
        for idx, val in enumerate(inVec):
            self.sensors[idx].activate(self.encode(val, mx, mn))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getOutput(self, mx=1, mn=-1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ pull the restored (non-normalized) output values from the network
            returned as a array
        """
        self.currentTime += 1
        return [self.decode(o.getActivation(self.currentTime), mx, mn) for o in self.outputs]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def train(self, desired, mx=1, mn=-1, trainingRate=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ perform a single training iteration on the network by specifying
            the desired values (as a sequence 'desired') corresponding to the
            current input.
        """
        for idx, o in enumerate(self.outputs):
            o.train(self.encode(desired[idx], mx, mn) - o.activation, trainingRate)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def trial(self, input):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ a trial is just the application of an input and returning the output
        """
        self.setInput(input)
        return self.getOutput()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def allocLayer(self, num, inputs, nElemClass=Neuron):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ create all the neurons at a particular layer. 'num' indicates how
            many neural elements to create and 'nElemClass' specifies the type
            of neural element to create. 'inputs' is an array of all neural
            elements in the prior layer and it is assumed here that each is
            connected to every neural element in this layer. (of course a
            weight of 0 is mathematically the same no connection.)
        """
        return [nElemClass(inputs) for i in range(num)] if num is not None else []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xmlLayer(self, xn, tag, layer):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        xnn = xn.add('<%s/>' % tag)
        for n in layer:
            xnn.add(n.asXmlNode())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loadLayer(self, xn, tag, layer, references, nElemClass=Neuron):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for cxml in xn.findChild(tag).nodes:
            cn = nElemClass().xmlLoad(cxml)
            references[cn.id] = cn
            layer.append(cn)
        return layer

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def resolveLayer(self, layer, references):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for n in layer:
            n.resolveRefs(references)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def asXmlNode(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ save as xml returning an xml node object
        """
        xn = xp.xmlNode('<neural_net formatVersion="%s" name="%s" numHidden="%d"/>' % (self.formatVersion, self.name, self.numHidden))
        self.xmlLayer(xn, 'sensors', self.sensors)
        self.xmlHidden(xn)
        self.xmlLayer(xn, 'outputs', self.outputs)
        return xn

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xmlLoad(self, xn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if xn['formatVersion'] != self.formatVersion:
            raise NNException('Bad XML File Format Revision. Expecting "%s"' % self.formatVersion)

        self.name = xn['name']
        self.numHidden = int(xn['numHidden'])

        references = {}
        self.loadLayer(xn, 'sensors', self.sensors, references, Sensor)
        self.loadXmlHidden(xn, references)
        self.loadLayer(xn, 'outputs', self.outputs, references)

        self.resolveHiddenRefs(references)
        self.resolveLayer(self.outputs, references)

        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def storeXmlHidden(self, xn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loadXmlHidden(self, xn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def resolveHiddenRefs(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass


#-------------------------------------------------------------------------------
class NeuralNetwork3Layer(NeuralNetwork):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name=None, inputNum=None,  outputNum=None, hiddenNum=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        NeuralNetwork.__init__(self, name, inputNum)
        self.numHidden = 1
        self.hiddens = self.allocLayer(hiddenNum, self.sensors)
        self.outputs = self.allocLayer(outputNum, self.hiddens)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xmlHidden(self, xn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.xmlLayer(xn, 'hiddens', self.hiddens)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loadXmlHidden(self, xn, references):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.loadLayer(xn, 'hiddens', self.hiddens, references)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def resolveHiddenRefs(self, references):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.resolveLayer(self.hiddens, references)


#-------------------------------------------------------------------------------
class NeuralNetworkNLayer(NeuralNetwork):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, name=None, inputNum=None, outputNum=None, *hiddenNums):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        NeuralNetwork.__init__(self, name, inputNum)
        self.numHidden = len(hiddenNums)
        self.hiddens = []

        input = self.sensors
        for num in hiddenNums:
            input = self.allocLayer(num, input)
            self.hiddens.append(input)

        self.outputs = self.allocLayer(outputNum, input)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xmlHidden(self, xn):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for idx, layer in enumerate(self.hiddens):
            self.xmlLayer(xn, 'hidden%d' % idx, layer)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def loadXmlHidden(self, xn, references):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for idx in range(self.numHidden):
            self.hiddens.append(self.loadLayer(xn, 'hidden%d' % idx, [], references))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def resolveHiddenRefs(self, references):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for hidden in self.hiddens:
            self.resolveLayer(hidden, references)


#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester
    return 0


if __name__ == "__main__":
    import pylib.osscripts as oss
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)


