package edu.uga.cs.digger.client;

import java.util.List;

/**
 * @author Kevin Warrick
 * @version 2013-02-18
 */
public class DiggerRequest {
	
	private String domain;
	private List<String> resolvers;
	private String type;
	private String flags;
	
	public DiggerRequest() { }
	
	public String getDomain() { return domain; }
	public List<String> getResolvers() { return resolvers; }
	public String getType() { return type; }
	public String getFlags() { return flags; }
	
	public String toString() {
		String fmt = "domain: %s\nresolvers: %s\ntype: %s\nflags: %s\n";
		return String.format(fmt, domain, resolvers.toString(), type, flags);
	}
}