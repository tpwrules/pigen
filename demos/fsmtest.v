/* Machine-generated using Migen */
module top(
	output reg active,
	output reg [2:0] bitno,
	input strobe,
	input sys_clk,
	input sys_rst
);

reg [1:0] state = 2'd0;
reg [1:0] next_state;
reg [2:0] bitno_next_value;
reg bitno_next_value_ce;


// Adding a dummy event (using a dummy signal 'dummy_s') to get the simulator
// to run the combinatorial process once at the beginning.
// synthesis translate_off
reg dummy_s;
initial dummy_s <= 1'd0;
// synthesis translate_on


// synthesis translate_off
reg dummy_d;
// synthesis translate_on
always @(*) begin
	active <= 1'd0;
	next_state <= 2'd0;
	bitno_next_value <= 3'd0;
	bitno_next_value_ce <= 1'd0;
	next_state <= state;
	case (state)
		1'd1: begin
			active <= 1'd1;
			if (strobe) begin
				bitno_next_value <= (bitno + 1'd1);
				bitno_next_value_ce <= 1'd1;
				if ((bitno == 3'd7)) begin
					next_state <= 2'd2;
				end
			end
		end
		2'd2: begin
			active <= 1'd0;
			next_state <= 2'd3;
		end
		2'd3: begin
			active <= 1'd0;
			if (strobe) begin
				next_state <= 1'd0;
				bitno_next_value <= 1'd0;
				bitno_next_value_ce <= 1'd1;
			end
		end
		default: begin
			active <= 1'd1;
			if (strobe) begin
				next_state <= 1'd1;
			end
		end
	endcase
// synthesis translate_off
	dummy_d <= dummy_s;
// synthesis translate_on
end

always @(posedge sys_clk) begin
	state <= next_state;
	if (bitno_next_value_ce) begin
		bitno <= bitno_next_value;
	end
	if (sys_rst) begin
		bitno <= 3'd0;
		state <= 2'd0;
	end
end

endmodule
