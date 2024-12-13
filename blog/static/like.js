// Botões de like dos posts
const likeButtons = document.querySelectorAll('.like-button');

likeButtons.forEach(button => {

    button.addEventListener('click', async (event) => {

        event.preventDefault(); // Evita comportamento padrão, se houver

        const postId = button.getAttribute('data-post-id');

        // URL para fazer a requisição para dar like
        const url = `/like/${postId}`;

        try {
            // Faz a requisição para o servidor usando fetch
            const response = await fetch(url, { method: 'GET' });

            if (response.ok) {

                // Retorna um json
                const data = await response.json();
                const likeCount = document.getElementById(`like-count-${postId}`);
                likeCount.innerText = data.like_count;

                // Atualizar o estado do botão
                if (data.liked)
                    button.classList.add('curtido');
                else
                    button.classList.remove('curtido');

            }

        } catch (error) {
            console.error('Erro:', error);
        }
    });

});