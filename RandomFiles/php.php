<?php
$my_email = "barbaracartomante59@gmail.com"; //fill in your own e-mail adress
?>

<?php
if (isset($_REQUEST['email'])) {
	//send email
	$email = $_REQUEST['email'] ;
	$subject = $_REQUEST['subject'] ;
	$message = $_REQUEST['message'] ;

	echo "<table class='table' width='50%'>
		<tr class='table_header'>
			<td>www.barbaracartomante.com dice: </td>
		</tr>
		<tr class='row1'>
			<td>";
				if ($email == "") {
					echo "ERRORE: Devi inserire un indirizzo e-mail valido<br>";
					echo "<input type='button' value='Back' onclick='goBack()' />";
					exit;
				}
				if ($subject == "") {
					echo "ERRORE: Devi inserire un argomento a tua scelta <br>";
					echo "<input type='button' value='Back' onclick='goBack()' />";
					exit;
				}
				if ($message == "") {
					echo "ERRORE: Devi inserire un messaggio in questo campo <br>";
					echo "<input type='button' value='Back' onclick='goBack()' />";
					exit;
				}

			mail($my_email, $subject,
			$message, "From:" . $email);
			echo "Ti ringrazio per avermi contattata.<br>Risponder&ograve; appena possibile.
			</td>
		</tr>
	</table>";
 
} else {

	echo "<form method='post' action='contact_form.php'>
		<table class='table' width='40%'>
			<tr class='table_header'>
				<td colspan='2'>Contattami Subito, Sono a Tua Completa Disposizione</td>
			</tr>
			<tr class='row1'>
				<td>E-mail:</td>
				<td>
					<input name='email' type='text' />
				</td>
			</tr>
			<tr class='row1'>
				<td>Argomento:</td>
				<td>
					<input name='subject' type='text' />
				</td>
			</tr>
			<tr class='row1'>
				<td valign='top'>Messaggio:</td>
				<td>
					<textarea name='message' rows='8' cols='40'></textarea>
				</td>
			</tr>
			<tr class='row1'>
				<td>&nbsp;</td>
				<td>
					<input type='submit' value='Invia Messaggio' />
				</td>
			</tr>
		</table>
	</form>";
}
?>


