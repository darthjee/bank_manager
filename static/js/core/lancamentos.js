$(function(){
	(function($){
		var baseUrl = '/bank/lancamentos/'+context.conta+'/';
		$.fn.bindNavigator = function(){
			var $inputs = $(this).find('input,select');
			
			function setDate(mes, ano){
				mes = mes ? mes : $inputs.filter('.mes').val();
				ano = ano ? ano : $inputs.filter('.ano').val();
				
				var url  = baseUrl+ano+'/';
				if (mes != 0)
					url += mes+'/';
				window.location.href=url;
			}
			function callDate(){
				setDate();
			}
			
			$inputs.eventBubble([{
				timeout : 1000,
				evt : 'selected',
				call:callDate
	        },{     
	            timeout : 0,
	            evt : 'selecting'
	        }]);
	        
	        $inputs.bind('change keypress', function(){
	        	setTimeout(function(){
	        		$inputs.trigger('selected');
	        	},100);
	        });
	        $inputs.bind('click', function(e){
	            $inputs.trigger('selecting');
	        });
	        
	        $(this).find('button.navigator').bind('click', function(e){
	        	e.preventDefault();
	        	var delta = Number($(this).attr('navigation'));
	        	
	        	var mes = context.mes||Math.abs(delta)==1?context.mes:1;
	        	var ano = context.ano;
	        	
	        	var d = new Date(ano, mes+delta-1);
	        	
	        	mes = context.mes||Math.abs(delta)==1?d.getMonth()+1:0;
	        	ano = d.getFullYear();
	        	
	        	setDate(mes, ano);
	        });
		};
		
		$('.filter').bindNavigator();
		
		$('table.lancamentos td.actions .confirmar').bind('click', function(){
			var $tr = $(this).parents('tr:eq(0)');
			var id = $tr.attr('transId').trim();
			var url = '/bank/transacoes/'+id+'/confirmar/';
			$.ajax({
				url:url,
				success:function(){
					$tr.addClass('confirmed').removeClass('not-confirmed');
				}
			});
		})
		
	})(jQuery);
});
