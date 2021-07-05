# Help

Hints and tips for building better threat models using FluenTM

## DataFlow $name has no data associated
DataFlows are a critical component in any threat model. They describe how data moves about a system. DataFlows have three mandetory parameters; *pitcher* and *catcher* define where the DataFlow originates from and is terminated, *name* is the unique name to use with the dataflow. In addition to these values, users are strongly encouraged to include the data that flows in this communication.

The *data* can just be a string that describes the data. Of course, this isn't very useful on it's own, as in a threat model we care a lot about how data is protected when it moves. To support this, FluenTM provides a number of wrappers to encapsulate data.

```python
# A basic DataFlow, useful for diagrams but not so good for helping with security decisions
DataFlow(Actor("Alice"), Actor("Bob"), "Secret message")
```
In the model above we've described Alice sending a "secret message" to Bob. This is a valid and useful dataflow but leads to predictable questions about how that message is communicated. To save time in the review, various transport types are supported in FluenTM.

```python
# A basic DataFlow, useful for diagrams but not so good for helping with security decisions
DataFlow(Actor("Alice"), Actor("Bob"), "Secret message", data=TLS(HTTP("PUT Message")))
```
The DataFlow above took only moments more to write, but expresses a lot more about the DataFlow.

Currently available Dataflow data types are listed below. They can be combined in any way.
* Plaintext
* HTTP
* HTTPBasicAuth
* TLS
* IPSEC
* TLSVPN
* MTLSVPN
* SIGV4

So, if you were making an SIGv4 signed API request to an AWS service, over a private IPSEC tunnel, you could model that below:
```python
IPSEC(TLS(HTTP(SIGV4("PUT create ec2-instance"))))
```

If you're just sending unencrypted data that can be modelled with Plaintext:
```python
Plaintext("DNS Lookup")
```
