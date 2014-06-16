package edu.uga.cs.digger.client;

import java.io.IOException;

import org.xbill.DNS.*;
import com.google.gson.Gson;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.AlreadyClosedException;

/**
 * @author Kevin Warrick
 * @version 2013-02-18
 * DNSResponseListener objects are responsible for receiving the 
 * DNS responses issued asynchronously by the dnsjava library.
 * 
 * Upon receiving a DNS response or an exception, a DiggerResponse
 * object is serialized as JSON and sent to RabbitMQ.
 */
public class DNSResponseListener implements ResolverListener {
	private DiggerResponse response;
	private Channel channel;
	
	public DNSResponseListener(String domain, String resolver, String flags, Channel channel) {
		this.response = new DiggerResponse(domain, resolver, flags);
		this.channel = channel;
	}
	
	@Override
	public void handleException(Object id, Exception e) {
		response.setError(e);
		response.setTime(System.currentTimeMillis() / 1000);
		send();
	}
	
	@Override
	public void receiveMessage(Object id, Message m) {
		response.setResponse(m.toWire());
		response.setTime(System.currentTimeMillis() / 1000);
		
		try { send(); }
		catch (AlreadyClosedException e){
			System.err.println("com.rabbitmq.client.AlreadyClosedException: " + response.getDomain());
		}
	}
	
	private void send() {
		try {
			byte[] body = new Gson().toJson(response).getBytes();
			channel.basicPublish("dns", "response", null, body);
		}
		catch (IOException ex) {
			System.err.println(ex);
		}
	}
}
