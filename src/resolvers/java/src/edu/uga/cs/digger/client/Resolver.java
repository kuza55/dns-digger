package edu.uga.cs.digger.client;

import java.io.IOException;
import java.util.concurrent.ArrayBlockingQueue;

import com.rabbitmq.client.*;
import org.apache.commons.cli.*;

/**
 * @author Kevin Warrick
 * @version 2013-02-18
 *	
 * Resolver is the main class responsible for parsing command-line arguments, 
 * connecting to the RabbitMQ server, registering the message handler, and throttling requests.
 * 
 *		 +--------------+          +------------------+
 *		 |   Resolver   |+-------+ |  MessageHandler  |
 *		 +--------------+          +------------------+
 *		                             +              +
 *		                             |     0..n     |
 *		                             |              |
 *		                +----------------------+    +
 *		                |  DNSResponseListener |
 *		                +----------------------+ 
 */
public class Resolver {
	
	private static String host, user, pass;
	private static Integer port, connectAttempts;
	
	private static Connection connection;
	private static Channel channel;
	
	public static void main(String[] args) throws IOException, InterruptedException {	
		connectAttempts = 0;
		parseArguments(args);
		connect();
		
		connection.addShutdownListener(new ShutdownListener() {
		    public void shutdownCompleted(ShutdownSignalException cause) {
				System.err.println(cause.toString());
				System.err.println("Reconnecting.");
				connect();
			}
		});
		
		ArrayBlockingQueue<Integer> tokenBucket = new ArrayBlockingQueue<Integer>(200);		
		channel.basicQos(25);
		channel.basicConsume("query", false, new MessageHandler(channel, tokenBucket));
		
		while (true) { 	
			/* throttle responses */
			for (int i = 0; i < 19; i++) { tokenBucket.offer(0); };
			Thread.sleep(100); 
		}		
	}
	
	/**
	 * Connect to the RabbitMQ server.
	 */
	private static void connect() {
		ConnectionFactory factory = new ConnectionFactory();
		factory.setUsername(user);
		factory.setPassword(pass);
		factory.setHost(host);
		factory.setPort(port);
		
		try {
			connection = factory.newConnection();
			channel = connection.createChannel();
		}
		catch (IOException ex) {
			connectAttempts += 1;
			long wait = (long) Math.min(600, Math.pow(connectAttempts, 2));
			System.err.println("Failed to connect, trying again in " + wait + " seconds.");
			
			try { Thread.sleep(wait * 1000); }
			catch (InterruptedException e) { Thread.currentThread().interrupt(); }
			connect();
		}
	}

	/**
	 * Parse arguments from the command-line.
	 * (e.g. host, port, user, and pass)
	 * @param args command-line arguments.
	 */
	private static void parseArguments(String[] args) {
		CommandLine cmd;
		Options options = new Options();
		CommandLineParser parser = new PosixParser();
		HelpFormatter formatter = new HelpFormatter();
		
		Option hostOpt = OptionBuilder.withArgName("host")
									  .hasArg()
									  .isRequired()
									  .withDescription("RabbitMQ server hostname")
									  .create("host");
									
		Option portOpt = OptionBuilder.withArgName("port")
									  .hasArg()
									  .isRequired()
									  .withDescription("RabbitMQ server port")
									  .create("port");
									
		Option userOpt = OptionBuilder.withArgName("user")
									  .hasArg()
									  .isRequired()
									  .withDescription("RabbitMQ server username")
									  .create("user");	
									
		Option passOpt = OptionBuilder.withArgName("pass")
									  .hasArg()
									  .isRequired()
									  .withDescription("RabbitMQ server password")
									  .create("pass");	

		options.addOption(hostOpt);
		options.addOption(portOpt);
		options.addOption(userOpt);
		options.addOption(passOpt);
		
		try {
			cmd = parser.parse(options, args);
			
			host = cmd.getOptionValue("host");
			port = new Integer(cmd.getOptionValue("port"));
			user = cmd.getOptionValue("user");
			pass = cmd.getOptionValue("pass");
		}	
		catch (ParseException ex) {
			System.err.println(ex.getMessage());
			formatter.printHelp("resolver", options);
			System.exit(2);
		}								
	}
}