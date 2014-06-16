package edu.uga.cs.digger.client;

import java.util.List;
import java.io.IOException;
import java.util.concurrent.ArrayBlockingQueue;

import org.xbill.DNS.*;
import com.google.gson.Gson;
import com.rabbitmq.client.*;
import org.apache.commons.cli.*;

/**
 * @author Kevin Warrick
 * @version 2013-02-18
 * 
 * MessageHandler is spawned by Resolver to handle RabbitMQ messages.
 * 
 * Upon receiving a message, MessageHandler convers the JSON into a
 * DiggerRequest object using Google's GSON library.
 *
 * MessageHandler then issues an asynchronous query for the domain on 
 * the local DNS resolvers and DNS resolvers specified in the request.
 *
 * Each request issued using dnsjava's SimpleResolver spawns a thread
 * DNSResponseListener, which is responsible for responding to the
 * request when and if a DNS response is received. 
 */
public class MessageHandler extends DefaultConsumer {
	
	private Channel channel;
	private ArrayBlockingQueue tokenBucket;
	String consumerTag;
	
	public MessageHandler(Channel channel, ArrayBlockingQueue tokenBucket) {
		super(channel);
		this.channel = channel;
		this.tokenBucket = tokenBucket;
	}
	
	@Override
	public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body)
		throws IOException {
		
		long deliveryTag = envelope.getDeliveryTag();
		
		DiggerRequest request = new Gson().fromJson(new String(body), DiggerRequest.class);
		
		String domain = request.getDomain();
		String type = request.getType();
		List<String> resolvers = request.getResolvers();
		String flags = request.getFlags();
		
		/* get local resolvers */
		ResolverConfig rc = new ResolverConfig();
		for (String host : rc.servers()) { resolvers.add(host); }
						
		for (String host : resolvers) {
			/* throttle */
			try {  tokenBucket.take(); 	}
			catch (InterruptedException e) { Thread.currentThread().interrupt(); }
			
			SimpleResolver resolver = new SimpleResolver(host);
			Record record = Record.newRecord(new Name(domain, Name.root), Type.value(type), DClass.IN);
			Message query = Message.newQuery(record);
		
			resolver.setTimeout(3);		
			resolver.sendAsync(query, new DNSResponseListener(domain, host, flags, channel));
		}
		
		channel.basicAck(deliveryTag, false);
	}
}