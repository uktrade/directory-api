def test_empty_object_returned(client):
    response = client.get('/activity-stream/')
    assert response.status_code == 200
    assert response.content == b'{}'
