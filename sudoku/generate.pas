const n=9;
type tarr = array[0..n] of array[0..n] of longint;
type field = record
	matrix:tarr;
	size,bwidth,bheight:longint;
end;
type point = array[0..1] of longint;
type tparr = array[0..(n*n)-1] of point;

function test_col(const arr:tarr; y0,x0:longint):boolean;
var y:longint;
begin
	test_col:=true;
	for y:=0 to n do
		if (arr[y][x0]=arr[y0][x0]) and (y<>y0) then begin test_col:=false; break; end;
end;

function test_row(const arr:tarr; y0,x0:longint):boolean;
var x:longint;
begin
	test_row:=true;
	for x:=0 to n do
		if (arr[y0][x]=arr[y0][x0]) and (x<>x0) then begin test_row:=false; break; end;
end;


function test_block(const f:field; y0,x0:longint):boolean;
var x,y:longint;
begin
	test_block:=true;
	for x:=(x0 div f.bwidth)*f.bwidth to ((x0 div (f.bwidth+1))*f.bwidth)-1 do
		for y:=(y0 div f.bheight)*f.bheight to ((y0 div (f.bheight+1))*f.bheight)-1 do
			if (y<>y0) and (x<>x0) and (f.matrix[y][x]=f.matrix[y0][x0]) then begin test_block:=false; exit;end;
end;

function check(const f:field; y0,x0:longint):boolean;
begin
	check:=false;
	if test_col(f.matrix,y0,x0) then
		if test_row(f.matrix, y0, x0) then
			if test_block(f, y0, x0) then
				check:=true;
end;

function generate(r:longint; const points:tparr; var f:field):boolean;
var x,y,i:longint;
begin
	{writeln(r);}

	if r=n*n then begin generate:=true; exit; end;
	x:=points[r][0];
	y:=points[r][1];
	for i:=1 to n do begin
		f.matrix[y][x]:=i;
		if check(f,y,x) then
			if generate(r+1,points,f) then begin generate:=true;exit;end;
	end;
	f.matrix[y][x]:=0;
	generate:=false;
end;

procedure write_to_file(f:field);
var x,y:longint;
var fdesc:text;
begin
	assign(fdesc, 'outp.txt');
	rewrite(fdesc);
	writeln(fdesc, f.size, ' ', f.bwidth, ' ', f.bheight);
	for y:=0 to n-1 do begin
		for x:=0 to n-1 do
			write(fdesc, f.matrix[y][x], ' ');
		writeln(fdesc,' ');
		end;
	close(fdesc);
end;

function generate_points():tparr;
var i,rr,x,y:longint;
var tmp:point;
var arr:tparr;
begin
	for i:=0 to (n*n)-1 do begin arr[i][0]:=i div n; arr[i][1]:=i mod n; end;
	for i := 0 to (n*n)-1 do begin
		rr := random((n*n)-1);
		tmp := arr[i];
		arr[i] := arr[rr];
		arr[rr] := tmp;
	end;
	generate_points:=arr;
end;

var f:field;
var a:tparr;
begin
	randomize;
	f.size:=n;
	f.bwidth:=3;
	f.bheight:=3;
	a:=generate_points;
	generate(0,a,f);
	write_to_file(f);

end.
