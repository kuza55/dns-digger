package edu.uga.cs.digger.client;

import org.xbill.DNS.utils.base64;

/**
 * @author Kevin Warrick
 * @version 2013-02-18
 */
public class DiggerResponse {
	
	private String domain;
	private String resolver;
	private String response;
	private String flags;
	private String error;
	private Long time;
		
	public DiggerResponse(String domain, String resolver, String flags) {
		this.domain = domain;
		this.resolver = resolver;
		this.flags = flags;
	}
	
	public void setResponse(byte[] r) {
		this.response = base64.toString(r);
	}
	
	public void setError(Exception e) {
 		this.error = e.getClass().getName();
	}
	
	public void setTime(Long t) {
		this.time = t;
	}
	
	public String getDomain() { return this.domain; }
	public String getResolver() { return this.resolver; }
	public String getResponse() { return this.response; }
	public String getError() { return this.error; }
	public String getFlags() { return this.flags; };
	public Long getTime() { return this.time; }
	
	public String toString() {
		String fmt = "domain: %s\nresolver: %s\ntime: %d\nresponse: %s\n";
		return String.format(fmt, domain, resolver, time, response);
	}
}