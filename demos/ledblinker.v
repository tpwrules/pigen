/* Machine-generated using Migen */
module top(
	output led,
	output reg cspl,
	output reg sspl,
	input sys_clk,
	input sys_rst
);

reg [25:0] counter = 26'd0;


// Adding a dummy event (using a dummy signal 'dummy_s') to get the simulator
// to run the combinatorial process once at the beginning.
// synthesis translate_off
reg dummy_s;
initial dummy_s <= 1'd0;
// synthesis translate_on

assign led = counter[25];

// synthesis translate_off
reg dummy_d;
// synthesis translate_on
always @(*) begin
	cspl <= 1'd0;
	if ((counter == 6'd37)) begin
		cspl <= 1'd1;
	end
// synthesis translate_off
	dummy_d <= dummy_s;
// synthesis translate_on
end

always @(posedge sys_clk) begin
	counter <= (counter + 1'd1);
	if ((counter == 10'd572)) begin
		sspl <= 1'd1;
	end else begin
		if ((counter == 10'd999)) begin
			sspl <= 1'd0;
		end
	end
	if (sys_rst) begin
		sspl <= 1'd0;
		counter <= 26'd0;
	end
end

endmodule
