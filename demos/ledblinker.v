/* Machine-generated using Migen */
module top(
	output led,
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

always @(posedge sys_clk) begin
	counter <= (counter + 1'd1);
	if (sys_rst) begin
		counter <= 26'd0;
	end
end

endmodule
