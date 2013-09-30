/* calls bootstro (tutorial) plugin */
    $(document).ready(function(){
        // $("#tutorial").click(function(){
            bootstro.start(".bootstro", {
                onComplete : function(params)
                {
                    // alert("Reached end of introduction with total " + (params.idx + 1)+ " slides");
                },
                onExit : function(params)
                {
                    // alert("Introduction stopped at slide #" + (params.idx + 1));
                },
            // });    
        });
        // $(".demo_stopOn").click(function(){
        //     alert('Clicking on the backdrop or Esc will NOT stop the show')
        //     bootstro.start('.bootstro', {stopOnBackdropClick : false, stopOnEsc:false});    
        // });
        // $(".demo_size1").click(function(){
        //     bootstro.start('.bootstro_size1');    
        // });
        // $(".demo_nonav").click(function(){
        //     bootstro.start('.bootstro', {
        //         nextButton : '',
        //         prevButton : '',
        //         finishButton : ''
        //     });    
        // });
        // $(".demo_ajax").click(function(){
        //     bootstro.start('', {
        //         url : './bootstro.json',
        //     });    
        // });
    });